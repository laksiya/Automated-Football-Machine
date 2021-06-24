///// POTENTIOMETER TO ENCODER ADC /////
///// Author: Laksiya B., March 2021////

const int N = 4;
const int track_data = 1;
const int resolution_level = 6;
const int pot_max = 855;
const int pot_min = 778;
const byte CLOCKOUT = 9; //Leonardo

int encoder_signal_A[N] = {0, 0, 1, 1};
int encoder_signal_B[N] = {0, 1, 0, 1};
int current_signals[2] = {0, 0};

uint8_t pinA = 9;
uint8_t pinB = 10;

int i = -1, prev_i = -1;
int count,input, difference, prev_input, index;

void setup() {
  Serial.begin(9600);
  pinMode(pinA, OUTPUT);
  pinMode(pinB, OUTPUT);
  count = analogRead(A0);

  // set up 8 MHz timer on CLOCKOUT (OC1A)
  pinMode (CLOCKOUT, OUTPUT); 
  // set up Timer 1
  TCCR1A = bit (COM1A0);  // toggle OC1A on Compare Match
  TCCR1B = bit (WGM12) | bit (CS10);   // CTC, no prescaling
  OCR1A =  0;       // output every cycle
}

void loop() {
  input = analogRead(A0);
  counter(input);
  find_valid_index();
  if (i != prev_i) {
    current_signals[0] = encoder_signal_A[i];
    current_signals[1] = encoder_signal_B[i];
    print_values();
    }
  digitalWrite(pinA, current_signals[0]);
  digitalWrite(pinB, current_signals[1]);
  prev_i = i;
  prev_input = input;
  delay(1000); //set to roboclaw clock time
}


void find_valid_index() {
  if (i >= N) {
    i = i % N;
  }
  if (i < 0) {
    while (i < 0) {
      i += N;
    }
  }
}

void counter(int potvalue) {
  if (track_data){
  Serial.println("---in counter ---");
  Serial.println("count: ");
  Serial.println(count);
  Serial.println("potvalue: ");
  Serial.println(potvalue);
  Serial.println("i: ");
  Serial.println(i);
  Serial.println("---out counter ---");
  }

  if(potvalue > pot_max){
    Serial.println("WARNING: potvalue above range 779-854");
    return;
    }
  if(potvalue < pot_min){
    Serial.println("WARNING: potvalue below range 779-854");
    return;
    }

  if (potvalue == count) {
    return;
  }
  else if (potvalue > count + resolution_level) {
    count+= resolution_level;
    i++;
  }
  else if (potvalue < count - resolution_level) {
    count-=resolution_level;
    i--;
  }
  return;
}

void print_values(){
    Serial.println("i: ");
    Serial.println(i);
    Serial.println("newA: ");
    Serial.println(encoder_signal_A[i]);
    Serial.println("newB: ");
    Serial.println(encoder_signal_B[i]);
    Serial.println(" ");
    Serial.println(" ");
  
 }