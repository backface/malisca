/*
  Arduino Poti Controller
  
  write smoothed analog readings from multiple pins to serial
  
  created 06 August 2010
  by Michael Aschauer <m@ash.to>
  
*/
 
const int numReadings = 10;
const int numPins = 3;

int ledpin = 13;

int readings[numPins][numReadings];
int total[numPins];
int avg_value[numPins];
int last_value[numPins];

int index = 0;
int i = 0, j = 0;

boolean changed = false;

void setup() 
{
  
  pinMode(ledpin, OUTPUT);
  Serial.begin(9600);
  
  for(i=0; i<numPins; i++){
    avg_value[i] = 0;
    total[i] = 0;  
    last_value[i] = 0; 
    for(j=0; j<numReadings; j++){ 
      readings[numPins][numReadings] = 0;
    }
  } 

} 


void loop()
{
  changed=false; 
 
  for(i=0; i<numPins; i++)
  {
      total[i] = total[i] - readings[i][index];
      readings[i][index]  = analogRead(i);
      total[i] = total[i] + readings[i][index];
      avg_value[i] = total[i] / numReadings;
      
      if ( abs(avg_value[i] - last_value[i]) > 1) 
      {
        changed = true;
        last_value[i] = avg_value[i];
      }        
      
  }

  index++;
  if (index >= numReadings)
    index = 0;
  
  
  if (changed) {
    Serial.print("read:");
    
    for(i=0;i<numPins;i++) {      
      Serial.print(avg_value[i]);
      Serial.print(";");   
    }
    Serial.print("\n");
    digitalWrite(ledpin, HIGH);
  }
  
  
  digitalWrite(ledpin, LOW);

}

