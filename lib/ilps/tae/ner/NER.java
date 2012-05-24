package ilps.tae.ner;


import java.util.*;
import ilps.tae.Tagger;

public abstract class NER
extends Tagger
{    
    public NER(Properties p) 
    throws Exception
    {
        super(p);
    } 

    protected void fillTypeMap(Map<String, String> TYPEMAP) 
    {
       TYPEMAP.put("LOC", "LOC");
       TYPEMAP.put("PER", "PER");
       TYPEMAP.put("ORG", "ORG");
       TYPEMAP.put("MISC","MISC");
    }
    
    public static void main(String[] args) 
    throws Exception
    {
       ilps.tae.Tagger.main(NER.class, args);
    }
}
