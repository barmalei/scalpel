package gravity.tae.pos;


import java.util.Properties;
import gravity.tae.Tagger;

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
       gravity.tae.Tagger.main(POS.class, args);
    }
}
