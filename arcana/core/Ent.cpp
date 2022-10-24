// ---   *   ---   *   ---
// deps

  #include <iostream>

// ---   *   ---   *   ---

extern "C" {

// ---   *   ---   *   ---

float rflut(void) {

  return

    static_cast<float> (rand())
  / static_cast<float> (RAND_MAX)

  ;

};

// ---   *   ---   *   ---

void rcolor(float* b,int sz) {

  for(int i=0;i<sz;i+=4) {

    b[i+0]=rflut();
    b[i+1]=rflut();
    b[i+2]=rflut();

    b[i+3]=1.0;

  };

};

void renit(void) {};

// ---   *   ---   *   ---

}; // extern "C"
