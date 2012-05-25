package gravity.tae.ner.stanford;

import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations.AnswerAnnotation;
import edu.stanford.nlp.util.StringUtils;

import java.util.*;
import java.io.*;

import gravity.tae.*;

public class NER
extends gravity.tae.ner.NER
{    
    private AbstractSequenceClassifier classifier; 
  
    public NER(Properties p) 
    throws Exception
    {
        super(p);
        String model =(p.getProperty("model") != null) ? p.getProperty("model") : "default";
        File   f     = getModelFile(model);

        Properties prop = new Properties();
        prop.setProperty("useTitle", "true");
        classifier = new CRFClassifier(prop);
        classifier.loadClassifier(f, prop);
    } 

    protected void doTagging(String text, TaggerListener listener)
    throws Exception
    {
        List<List<CoreLabel>> out = classifier.classify(text);       
        for (List<CoreLabel> sentence : out) 
        {        
          for (CoreLabel word : sentence) 
          {       
             int b = word.beginPosition();
             listener.newTokenRecognized(word.word(), b, 
                                         word.endPosition() - b, 
                                         (String)word.get(AnswerAnnotation.class));
          }       
        }
    }
    
    protected void fillTypeMap(Map<String, String> TYPEMAP)
    {
       TYPEMAP.put("LOCATION",     "LOC" );
       TYPEMAP.put("PERSON",       "PER" );
       TYPEMAP.put("ORGANIZATION", "ORG" );
       TYPEMAP.put("MISC",         "MISC");
       TYPEMAP.put("O", "O");
    }
    
    public static void train(String propertiesFile)
    throws Exception
    {
        Properties p = new Properties();
        p.load(new java.io.FileInputStream(propertiesFile));        
        CRFClassifier c = new CRFClassifier(p);
        c.train();
    }
    
    public static void main(String[] args) 
    throws Exception
    {
       gravity.tae.ner.NER.main(NER.class, args);
      // train("lib/gravity/tae/ner/stanford2/conll.2002.train.properties");
    }
}
