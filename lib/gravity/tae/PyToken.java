package gravity.tae;


public class PyToken
{
    private static int allocate_bit_value = 1;
    
    private static final  int _allocate_bit() {
        allocate_bit_value = allocate_bit_value << 1;
        return allocate_bit_value;  
    }

    public static final int POS_PUNCT     = _allocate_bit(); 
    public static final int POS_VERB      = _allocate_bit();
    public static final int POS_ADVERB    = _allocate_bit();
    public static final int POS_PREP      = _allocate_bit();
    public static final int POS_CONJ      = _allocate_bit();
    public static final int POS_ART       = _allocate_bit();
    public static final int POS_NOUN      = _allocate_bit();
    public static final int POS_NUM       = _allocate_bit();
    public static final int POS_ADJ       = _allocate_bit();

    public static final int STR_SENTENSE  = _allocate_bit();
    public static final int STR_ARTICLE   = _allocate_bit();
    public static final int STR_PARAGRAPH = _allocate_bit();
     
    public static final int NE_ORG        = _allocate_bit();
    public static final int NE_LOC        = _allocate_bit();
    public static final int NE_PER        = _allocate_bit();
    public static final int NE_MISC       = _allocate_bit();
    
    private int offset = -1, len = 0, type = 0;
    private String text;
    
    public PyToken(String text, int offset, int len, int type) 
    {
       this.text = text;
       this.offset = offset;
       this.len = len;
       this.type = type;
    }
  
    public String getText() {
      return text;
    }

    public int getOffset() {
      return offset;
    }
    
    public int getLen() {
      return len;
    }

    public int getType() {
      return type;
    }
    
    public String toString() {
      return text;
    }
}
