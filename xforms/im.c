
// ---   *   ---   *   ---
// deps

  #include <stdlib.h>
  #include <stddef.h>

  #include <stdio.h>

// ---   *   ---   *   ---

typedef struct {

  size_t top;
  size_t buff_sz;

  size_t buff[];

} stack;

// ---   *   ---   *   ---

size_t pop(stack* s) {
  return s->buff[--s->top];

};

void push(stack* s,size_t v) {
  s->buff[s->top++]=v;

};

// ---   *   ---   *   ---

typedef struct {

  size_t sz_x;
  size_t sz_y;
  size_t chan;

  float buff[];

} Image;

// ---   *   ---   *   ---

static Image** BUFF_ARRAY;
static stack* BUFF_SLOT_STACK=NULL;

// ---   *   ---   *   ---

void nit(size_t size) {

  BUFF_SLOT_STACK=(stack*) malloc(
    sizeof(stack)
  + sizeof(size_t)*size

  );

  BUFF_SLOT_STACK->buff_sz=size;
  BUFF_SLOT_STACK->top=0;

  BUFF_ARRAY=(Image**) malloc(
    sizeof(Image*)*size

  );

// ---   *   ---   *   ---

  for(

    size_t i=0;
    i<BUFF_SLOT_STACK->buff_sz;

    i++

  ) {

    push(BUFF_SLOT_STACK,i);
    BUFF_ARRAY[i]=NULL;

  };

};

// ---   *   ---   *   ---

void del(void) {

  for(

    size_t i=0;
    i<BUFF_SLOT_STACK->buff_sz;

    i++

  ) {

    if(BUFF_ARRAY[i]!=NULL) {
      free(BUFF_ARRAY[i]);

    };

  };

// ---   *   ---   *   ---

  if(BUFF_ARRAY!=NULL) {
    free(BUFF_ARRAY);

  };

  if(BUFF_SLOT_STACK!=NULL) {
    free(BUFF_SLOT_STACK);

  };

};

// ---   *   ---   *   ---

float* get_buff(size_t idex) {
  return BUFF_ARRAY[idex]->buff;

};

// ---   *   ---   *   ---

size_t take(

  size_t sz_x,
  size_t sz_y,
  size_t chan,

  float* pixels

) {

  size_t idex=pop(BUFF_SLOT_STACK);

  Image* im=BUFF_ARRAY[idex]=(Image*) malloc(
    sizeof(Image)*(sizeof(float)*sz_x*sz_y*chan)

  );

  im->sz_x=sz_x;
  im->sz_y=sz_y;
  im->chan=chan;

// ---   *   ---   *   ---

  for(size_t y=0;y<sz_y;y++) {
    for(size_t x=0;x<sz_x;x++) {

      im->buff[x+(sz_x*y)+0]=*pixels++;
      im->buff[x+(sz_x*y)+1]=*pixels++;
      im->buff[x+(sz_x*y)+2]=*pixels++;
      im->buff[x+(sz_x*y)+3]=*pixels++;

    };

  };

// ---   *   ---   *   ---

  return idex;

};

// ---   *   ---   *   ---
