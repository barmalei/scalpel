package ilps.tae.pos;


import java.util.Properties;
import ilps.tae.Tagger;

public abstract class POS
extends Tagger
{    
    public POS(Properties p) 
    throws Exception
    {
        super(p);
    } 

    public static void main(String[] args) 
    throws Exception
    {
       ilps.tae.Tagger.main(POS.class, args);
    }
}
