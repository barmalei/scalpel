package ilps.tae.ner.lbj;

import java.io.*;
import java.util.*;

import lbj.NETaggerLevel1;
import lbj.NETaggerLevel2;
import LBJ2.parse.LinkedVector;
import LBJ2.classify.Classifier;
import LbjTagger.BracketFileManager;
import LbjTagger.NETester;
import LbjTagger.NEWord;
import LbjTagger.Parameters;

import ilps.tae.*;


public class NER
extends ilps.tae.ner.NER
{    
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
        Parameters.readConfigAndLoadExternalData(modelFile.getAbsolutePath());
    } 

    public void doTagging(String text, TaggerListener listener)
    throws Exception
    {
        NETaggerLevel1 tagger1 = new NETaggerLevel1();
        String path1 = resolvePath(Parameters.pathToModelFile + ".level1").getAbsolutePath();
        String path2 = resolvePath(Parameters.pathToModelFile + ".level2").getAbsolutePath();
        tagger1=(NETaggerLevel1)Classifier.binaryRead(path1);
        NETaggerLevel2 tagger2 = new NETaggerLevel2();
        tagger2=(NETaggerLevel2)Classifier.binaryRead(path2);
        
    	Vector<LinkedVector> data=BracketFileManager.parseText(text);
    	NETester.annotateBothLevels(data, tagger1, tagger2);

        for(int i=0;i < data.size(); i++){
            LinkedVector vector = data.elementAt(i);

            String        type   = null;
            StringBuilder entity = null;
            int           loc = -1, len = -1; 
            String[] predictions = new String[vector.size()];
            for(int j = 0;j < vector.size();j++){
            	predictions[j] = bilou2bio(((NEWord)vector.get(j)).neTypeLevel2);
            }
            
            entity = new StringBuilder();
            for(int j = 0; j < vector.size(); j++)
            { 
                NEWord w  = (NEWord)vector.get(j);
                String ww = w.form.trim();
                
            	if (predictions[j].startsWith("B-") || 
            		( j > 0 && predictions[j].startsWith("I-") && (!predictions[j-1].endsWith(predictions[j].substring(2)))))
            	{
            		type = predictions[j].substring(2);
            	}
            	
            	if (type != null) {
            	    if (entity.length() > 0) { 
            	        if (ww.charAt(0) != '\'') entity.append(' ');
                        // System.err.println("APPEND for " + entity.toString() + " and " + w.form);
            	    }
            	    else {
            	        loc = w.start;
            	        len = w.end - loc + 1;
            	    }
            	    entity.append(ww);
        	    }
            	
            	if(type != null){
            		boolean close=false;
            		if ( j==vector.size()-1 || 
            		     predictions[j+1].startsWith("B-") ||
            		     predictions[j+1].equals("O") || 
            		     (predictions[j+1].indexOf('-') >-1 && (!predictions[j].endsWith(predictions[j+1].substring(2)))))
            		{
                        listener.newTokenRecognized(entity.toString(), loc, len, type);
            			type = null;
            			loc = len = -1;
            			entity = new StringBuilder();
            		}
            	}
            }
        }
    }
    
    private String bilou2bio(String prediction){
    	if(Parameters.taggingScheme.equalsIgnoreCase(Parameters.BILOU)){
    		if(prediction.startsWith("U-"))
    			prediction="B-"+prediction.substring(2);
    		if(prediction.startsWith("L-"))
    			prediction="I-"+prediction.substring(2);
    	}
    	return prediction;
    }

    public static void main(String[] args) 
    throws Exception
    {
       //train(new File("/Users/avishneu/projects/tae/lib/ilps/tae/corpus/conll.nl.train"), 
         //    new File("/Users/avishneu/projects/tae/lib/ilps/tae/corpus/conll.nl.testa"), 
           //  new File("/Users/avishneu/projects/tae/lib/ilps/tae/corpus/result.nl"));


        ilps.tae.ner.NER.main(NER.class, args);


     //  System.err.println(":::" + (Character.getType('-') == Character.CONNECTOR_PUNCTUATION) );
       
       // NER n = new NER(new Properties());
       // String text = "A tsunami warning issued for north-eastern Japan after an earthquake with a magnitude of 7.1 has now been lifted, Japanese NHK TV says. Workers at the Fukushima Daiichi nuclear plant damaged in last month's quake and tsunami were evacuated. However, officials at the plant said there was no detectable effect there or at other nuclear plants in the region. The Japanese authorities ordered a general evacuation from the warning zone.\"Based on all available data, a destructive Pacific-wide tsunami is not expected,\" the Pacific Tsunami Warning Centre said on its website. But it warned: \"Earthquakes of this size sometimes generate local tsunamis that can be destructive along coasts located within 100km of the earthquake epicentre.\"There was no threat to Hawaii, it added.";
       // n.doRecognition(text, new NERListenerDebug());
    }
}
