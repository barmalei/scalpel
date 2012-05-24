package ilps.tae.pos.stanford;

import java.io.StringReader;
import java.io.FileReader;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.Map;
import java.util.HashMap;

import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;

import ilps.tae.*;


public class POS
extends ilps.tae.pos.POS
{    
    private MaxentTagger tagger; 
  
    public POS(Properties p) 
    throws Exception
    {
        super(p);
        File f = (p.getProperty("model") != null) ? getModelFile(p.getProperty("model"))
                                                  : getModelFile("default");
        tagger = new MaxentTagger(f.getAbsolutePath());
    } 

    protected void doTagging(String text, TaggerListener listener)
    throws Exception
    {
        @SuppressWarnings("unchecked")
        List sentences = tagger.tokenizeText(new StringReader(text)); 
        for (Object sentence : sentences) {
            ArrayList<TaggedWord> tSentence = tagger.tagSentence((List)sentence);
            for (TaggedWord word : tSentence) {
                int offset = word.beginPosition();
                listener.newTokenRecognized(word.word(), 
                                            offset, 
                                            word.endPosition() - offset, 
                                            word.tag());
            }
        }
    }
    
    protected String mapType(String type) {
        return type;
    }
    
    public static void main(String[] args) 
    throws Exception
    {
        ilps.tae.pos.POS.main(POS.class, args);
    }
}
