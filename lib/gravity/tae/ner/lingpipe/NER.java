package gravity.tae.ner.lingpipe;

import com.aliasi.chunk.*;

import com.aliasi.corpus.ObjectHandler;
import com.aliasi.corpus.StringParser;
import com.aliasi.corpus.Handler;

import com.aliasi.tag.LineTaggingParser;
import com.aliasi.tag.Tagging;

import com.aliasi.tokenizer.IndoEuropeanTokenizerFactory;
import com.aliasi.tokenizer.TokenizerFactory;

import com.aliasi.util.AbstractExternalizable;
import com.aliasi.util.Streams;
import com.aliasi.util.Compilable;

import com.aliasi.hmm.HmmCharLmEstimator;
import com.aliasi.hmm.AbstractHmmEstimator;

import java.io.*;
import java.util.*;
import java.net.*;

import gravity.tae.*;

public class NER
extends gravity.tae.ner.NER
{    
    static final int     NUM_CHUNKINGS_RESCORED = 64;
    static final int     MAX_N_GRAM = 12;
    static final int     NUM_CHARS = 256;
    static final double  LM_INTERPOLATION = MAX_N_GRAM; // default behavior
    static final boolean SMOOTH_TAGS = true;

    static class Conll2002ChunkTagParser
    extends StringParser<ObjectHandler<Chunking>> 
    {
        private LineTaggingParser mParser;
        private TagChunkCodec     mCodec;
        
        Conll2002ChunkTagParser() {
            mParser = new LineTaggingParser("(\\S+)\\s(\\S+\\s)?(O|[B|I]-\\S+)", // token ?posTag entityTag
                                             1, 3, "-DOCSTART(.*)", "\\A\\Z");
            mCodec  = new BioTagChunkCodec(null, false, "B-", "I-", "O");
        }
        
        public void parseString(char[] cs, int start, int end) {
            mParser.parseString(cs,start,end);
        }

        public void setHandler(ObjectHandler<Chunking> handler) {
            ObjectHandler<Tagging<String>> taggingHandler = TagChunkCodecAdapters.chunkingToTagging(mCodec,handler);
            mParser.setHandler(taggingHandler);
        }
    }

    //  generate HMM training model for CoNLL2002 data
    public static void hmm_train(File trainFile, File devFile, File modelFile, StringParser parser)
    throws Exception
    {
        CharLmHmmChunker  chunkerEstimator = new CharLmHmmChunker(IndoEuropeanTokenizerFactory.INSTANCE, 
                                                                  new HmmCharLmEstimator(MAX_N_GRAM,NUM_CHARS,LM_INTERPOLATION));
        train(trainFile, devFile, modelFile, chunkerEstimator, parser);
    }
    
    public static void lm_train(File trainFile, File devFile, File modelFile, StringParser parser)
    throws Exception
    {
        CharLmRescoringChunker chunkerEstimator = new CharLmRescoringChunker( IndoEuropeanTokenizerFactory.INSTANCE,
                                                                              NUM_CHUNKINGS_RESCORED,
                                                                              MAX_N_GRAM,NUM_CHARS,
                                                                              LM_INTERPOLATION);
        train(trainFile, devFile, modelFile, chunkerEstimator, parser);
        
    }

    //  generate rescoring training model for CoNLL2002 data
    public static void train(File trainFile, File devFile, File modelFile, Compilable estimator, StringParser parser)
    throws Exception
    {
        parser.setHandler((Handler)estimator);
        parser.parse(trainFile);
        parser.parse(devFile);
        AbstractExternalizable.compileTo(estimator, modelFile);   
    }

    private File modelFile = null;
    
    public NER(Properties p) 
    throws Exception
    {
        super(p);
        if (p.getProperty("model") != null) {
            modelFile = getModelFile(p.getProperty("model"));
        }
        else {
            modelFile = getModelFile("default");
        }
    } 

    protected void doTagging(String text, TaggerListener listener)
    throws Exception
    {
        Chunker chunker = (Chunker) AbstractExternalizable.readObject(modelFile);    
    
        Chunking    chunking = chunker.chunk(text);
        Set<Chunk>  chunkSet = chunking.chunkSet();
        for (Chunk chunk: chunkSet)
        {
           int   start = chunk.start(), end = chunk.end();
           listener.newTokenRecognized(text.substring(start, end), 
                                       start, 
                                       end - start, 
                                       chunk.type());
        }
    }
    
    //  !!!
    //  This evaluation code procides better result than using CoNLL collection as plain text and passing it as an imput
    //  Probably the cauase is Linpipe uses special CoNLL parser which can improve tokenization 
    //  It is still has to be clarified. 
    //  !!!
    public static void es_eval(String model, String dataFile)
    throws Exception
    {
        AbstractCharLmRescoringChunker chunker   = (AbstractCharLmRescoringChunker)AbstractExternalizable.readObject(new File(model));
        ChunkerEvaluator               evaluator = new ChunkerEvaluator(chunker);
        Conll2002ChunkTagParser parser = new Conll2002ChunkTagParser();
        parser.setHandler(evaluator);
        parser.parse(new File(dataFile));
        System.err.println(evaluator.toString());
    }
    
    
    public static void main(String[] args) 
    throws Exception
    {
        // System.err.println("1");
        // lm_train(new File("/Users/avishneu/projects/tae/lib/corpora/CoNLL/2002/data/esp.train"), 
        //           new File("/Users/avishneu/projects/tae/lib/corpora/CoNLL/2002/data/esp.testa"), 
        //           new File("/Users/avishneu/projects/tae/lib/corpora/CoNLL/2002/esp.result.nl"),
        //           new Conll2002ChunkTagParser());
        // System.err.println("2");

        // System.err.println("1");
        // hmm_train(new File("/Users/avishneu/projects/tae/lib/corpora/CoNLL/2003/data/eng.train.2002"), 
        //           new File("/Users/avishneu/projects/tae/lib/corpora/CoNLL/2003/data/eng.testa.2002"), 
        //           new File("/Users/avishneu/projects/tae/lib/corpora/CoNLL/2003/conll.2002.en.hmm"),
        //           new Conll2002ChunkTagParser());
        // System.err.println("2");
    
        gravity.tae.ner.NER.main(NER.class, args);
       
       // es_eval("/Users/avishneu/projects/tae/lib/gravity/tae/ner/lingpipe/es.conll.2002-4.0.0.lm",
       //         "/Users/avishneu/projects/tae/lib/corpora/CoNLL/2002/data/esp.testb");

       // es_eval("/Users/avishneu/projects/tae/lib/gravity/tae/ner/lingpipe/en.conll.2002-4.0.0.lm",
       //         "/Users/avishneu/projects/tae/lib/corpora/CoNLL/2003/data/eng.testb.2002");
    }
}
