// ================================================================
// ESP-32 + ACS712 電流感測器測試程式
// ================================================================
// 
// 接線說明 (Wiring):
// - ACS712 VCC  -> ESP-32 5V (或 3.3V，視模組而定)
// - ACS712 GND  -> ESP-32 GND  
// - ACS712 OUT  -> ESP-32 GPIO34 (ADC1_CH6)
// 
// ACS712 型號規格:
// - ACS712-20A: ±20A, 靈敏度 100mV/A
// 
// 使用說明:
// 1. 在 Arduino IDE 中開啟此檔案
// 2. 選擇開發板: ESP32 Dev Module
// 3. 選擇正確的 COM Port
// 4. 上傳程式到 ESP-32
// 5. 開啟序列埠監控視窗 (115200 baud)
// ================================================================

#include <WiFi.h>
#include <HTTPClient.h>

// ==================== 設定區 ====================
#define ACS712_PIN 34           // ACS712 輸出腳位
#define VREF 5.0               // 參考電壓 (V)
#define ADC_RESOLUTION 12      // ADC 解析度 (bits)
#define ADC_MAX 4095           // ADC 最大值 (2^12 - 1)

// Wi‑Fi / HTTP 設定
const char* WIFI_SSID = "Ethanlin";
const char* WIFI_PASSWORD = "00000000";
// 請填入執行 simple_number_server.py 的電腦 IP，不可使用 localhost
const char* SERVER_URL = "http://172.20.10.2:8001/number";

// 選擇 ACS712 型號 
#define ACS712_20A          // ±20A, 靈敏度 100mV/A

// 設定靈敏度
#ifdef ACS712_05A
  #define SENSITIVITY 0.185    // 185mV/A
  #define SENSOR_NAME "ACS712-05A"
#elif defined(ACS712_20A)
  #define SENSITIVITY 0.100    // 100mV/A
  #define SENSOR_NAME "ACS712-20A"
#elif defined(ACS712_30A)
  #define SENSITIVITY 0.066    // 66mV/A
  #define SENSOR_NAME "ACS712-30A"
#else
  #define SENSITIVITY 0.185    // 預設使用 05A
  #define SENSOR_NAME "ACS712-05A (預設)"
#endif

// ==================== 全域變數 ====================
float zeroVoltage = VREF / 2.0;  // 零點電壓 (無電流時的輸出電壓)
bool isCalibrated = false;        // 是否已校準

// ==================== ACS712 類別 ====================
class ACS712 {
  private:
    int pin;
    float sensitivity;
    float vref;
    int adcMax;
    
  public:
    // 建構子
    ACS712(int adcPin, float sens, float v, int maxVal) {
      pin = adcPin;
      sensitivity = sens;
      vref = v;
      adcMax = maxVal;
    }
    
    // 讀取 ADC 原始值
    int readADC() {
      return analogRead(pin);
    }
    
    // 讀取電壓值 (V)
    float readVoltage() {
      int adcValue = readADC();
      float voltage = (adcValue / (float)adcMax) * vref;
      return voltage;
    }
    
    // 校準零點
    void calibrate(int samples = 100) {
      Serial.println("\n========================================");
      Serial.print("開始校準零點 (取樣 ");
      Serial.print(samples);
      Serial.println(" 次)...");
      Serial.println("請確保沒有電流通過感測器!");
      
      float total = 0;
      
      for (int i = 0; i < samples; i++) {
        total += readVoltage();
        delay(10);
        
        // 顯示進度
        if ((i + 1) % 20 == 0) {
          Serial.print("進度: ");
          Serial.print(i + 1);
          Serial.print("/");
          Serial.println(samples);
        }
      }
      
      zeroVoltage = total / samples;
      isCalibrated = true;
      
      Serial.println("校準完成!");
      Serial.print("零點電壓: ");
      Serial.print(zeroVoltage, 4);
      Serial.println(" V");
      Serial.println("========================================\n");
    }
    
    // 讀取電流值 (A)
    float readCurrent(int samples = 10) {
      float total = 0;
      
      for (int i = 0; i < samples; i++) {
        float voltage = readVoltage();
        total += voltage;
        delay(5);
      }
      
      float avgVoltage = total / samples;
      
      // 計算電流: I = (V - V_zero) / Sensitivity
      float current = (avgVoltage - zeroVoltage) / sensitivity;
      
      return current;
    }
    
    // 讀取詳細資訊
    void readDetails(int samples = 10) {
      int adcValue = readADC();
      float voltage = readVoltage();
      float current = readCurrent(samples);
      
      Serial.print("ADC值: ");
      Serial.print(adcValue);
      Serial.print(" | 電壓: ");
      Serial.print(voltage, 4);
      Serial.print(" V | 電流: ");
      Serial.print(current, 3);
      Serial.print(" A (");
      Serial.print(current * 1000, 1);
      Serial.println(" mA)");
    }
};

// ==================== 建立 ACS712 物件 ====================
ACS712 sensor(ACS712_PIN, SENSITIVITY, VREF, ADC_MAX);

// ==================== 測試模式變數 ====================
int testMode = 0;  // 0=待機, 1=基本測試, 2=詳細測試, 3=統計測試
unsigned long lastReadTime = 0;
const unsigned long readInterval = 1000;  // 讀取間隔 (ms)

// 統計測試用變數
float readings[30];
int readingIndex = 0;
bool collectingStats = false;

// ==================== 網路功能 ====================
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("連線 Wi-Fi");
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 30) {
    delay(500);
    Serial.print(".");
    retry++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi 已連線, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi 連線失敗，HTTP 傳送將跳過");
  }
}

void postLevel(int value, const char* source) {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{\"value\":" + String(value) + ",\"source\":\"" + String(source) + "\"}";
  http.POST(payload);
  http.end();
}

// ==================== 輸出等級換算 ====================
// 將電流(mA)分為 1~8 等級：範圍 -100~100，每級 25mA，超出範圍會夾到端點
int currentToLevel(float current_mA) {
  float clamped = current_mA;
  if (clamped > 100.0) clamped = 100.0;
  if (clamped < -100.0) clamped = -100.0;

  int level = (int)((clamped + 100.0) / 25.0) + 1;
  if (level < 1) level = 1;
  if (level > 8) level = 8;
  return level;
}

// ==================== setup() ====================
void setup() {
  // 初始化序列埠
  Serial.begin(115200);
  delay(1000);
  
  // 設定 ADC
  analogReadResolution(ADC_RESOLUTION);
  pinMode(ACS712_PIN, INPUT);
  
  // 顯示歡迎訊息
  Serial.println("\n\n");
  Serial.println("========================================");
  Serial.println("ESP-32 + ACS712 電流感測器測試程式");
  Serial.println("Arduino IDE 版本");
  Serial.println("========================================");
  Serial.print("感測器型號: ");
  Serial.println(SENSOR_NAME);
  Serial.print("靈敏度: ");
  Serial.print(SENSITIVITY * 1000, 0);
  Serial.println(" mV/A");
  Serial.print("ADC 腳位: GPIO");
  Serial.println(ACS712_PIN);
  Serial.print("參考電壓: ");
  Serial.print(VREF);
  Serial.println(" V");
  Serial.println("========================================\n");

  // 連線 Wi‑Fi
  connectWiFi();
  
  // 自動校準
  Serial.println("5 秒後自動開始校準...");
  delay(5000);
  sensor.calibrate(100);
  
  // 顯示選單
  showMenu();
}

// ==================== loop() ====================
void loop() {
  // 檢查序列埠輸入
  if (Serial.available() > 0) {
    char input = Serial.read();
    
    // 清除緩衝區
    while (Serial.available() > 0) {
      Serial.read();
    }
    
    handleInput(input);
  }
  
  // 執行測試
  if (testMode == 1) {
    // 基本測試
    if (millis() - lastReadTime >= readInterval) {
      lastReadTime = millis();
      testBasic();
    }
  }
  else if (testMode == 2) {
    // 詳細測試
    if (millis() - lastReadTime >= readInterval) {
      lastReadTime = millis();
      testDetailed();
    }
  }
  else if (testMode == 3 && collectingStats) {
    // 統計測試
    if (readingIndex < 30) {
      if (millis() - lastReadTime >= 500) {
        lastReadTime = millis();
        collectStatistics();
      }
    } else {
      showStatistics();
      collectingStats = false;
      testMode = 0;
      Serial.println("\n按任意鍵返回選單...");
    }
  }
}

// ==================== 顯示選單 ====================
void showMenu() {
  Serial.println("\n========================================");
  Serial.println("請選擇測試模式:");
  Serial.println("========================================");
  Serial.println("1. 基本測試 - 輸出等級 1~8 (僅數字)");
  Serial.println("2. 詳細測試 - 數值串流 + 等級 (僅數字)");
  Serial.println("3. 統計測試 - 數據分析 (等級)");
  Serial.println("C. 重新校準");
  Serial.println("M. 顯示選單");
  Serial.println("========================================");
  Serial.println("請輸入選項 (1/2/3/C/M):");
}

// ==================== 處理輸入 ====================
void handleInput(char input) {
  input = toupper(input);  // 轉換為大寫
  
  switch (input) {
    case '1':
      testMode = 1;
      Serial.println("\n>>> 開始基本測試: 僅輸出等級 1~8 (按 0 停止)");
      Serial.println("----------------------------------------");
      break;
      
    case '2':
      testMode = 2;
      Serial.println("\n>>> 開始詳細測試: 僅輸出數字 CSV (time_s,adc,voltage_v,level) (按 0 停止)");
      Serial.println("----------------------------------------");
      break;
      
    case '3':
      testMode = 3;
      collectingStats = true;
      readingIndex = 0;
      Serial.println("\n>>> 開始統計測試 (收集 30 筆數據)");
      Serial.println("----------------------------------------");
      break;
      
    case 'C':
      testMode = 0;
      sensor.calibrate(100);
      showMenu();
      break;
      
    case 'M':
      testMode = 0;
      showMenu();
      break;
      
    case '0':
      testMode = 0;
      collectingStats = false;
      Serial.println("\n測試停止");
      showMenu();
      break;
      
    default:
      if (testMode == 0) {
        Serial.println("無效選項，請重新輸入!");
      }
      break;
  }
}

// ==================== 基本測試 ====================
void testBasic() {
  float current = sensor.readCurrent(20);
  float current_mA = current * 1000.0;
  int level = currentToLevel(current_mA);
  Serial.println(level);
  postLevel(level, "basic");
}

// ==================== 詳細測試 ====================
void testDetailed() {
  int adcValue = sensor.readADC();
  float voltage = sensor.readVoltage();
  float current = sensor.readCurrent(20);
  float current_mA = current * 1000.0;
  int level = currentToLevel(current_mA);
  
  float time_sec = millis() / 1000.0;

  Serial.print(time_sec, 2);
  Serial.print(",");
  Serial.print(adcValue);
  Serial.print(",");
  Serial.print(voltage, 4);
  Serial.print(",");
  Serial.println(level);
  postLevel(level, "detailed");
}

// ==================== 收集統計數據 ====================
void collectStatistics() {
  float current = sensor.readCurrent(20);
  float current_mA = current * 1000.0;
  int level = currentToLevel(current_mA);
  
  readings[readingIndex] = current;
  Serial.println(level);
  postLevel(level, "stats_sample");
  
  readingIndex++;
}

// ==================== 顯示統計結果 ====================
void showStatistics() {
  // 計算統計值
  float sum = 0;
  float maxCurrent = readings[0];
  float minCurrent = readings[0];
  
  for (int i = 0; i < 30; i++) {
    sum += readings[i];
    if (readings[i] > maxCurrent) maxCurrent = readings[i];
    if (readings[i] < minCurrent) minCurrent = readings[i];
  }
  
  float avgCurrent = sum / 30.0;
  float peakToPeak = maxCurrent - minCurrent;

  int avgLevel = currentToLevel(avgCurrent * 1000.0);
  int maxLevel = currentToLevel(maxCurrent * 1000.0);
  int minLevel = currentToLevel(minCurrent * 1000.0);
  int p2pLevel = currentToLevel(peakToPeak * 1000.0);

  // 僅輸出數字 (level): avg,max,min,peak_to_peak
  Serial.print(avgLevel);
  Serial.print(",");
  Serial.print(maxLevel);
  Serial.print(",");
  Serial.print(minLevel);
  Serial.print(",");
  Serial.println(p2pLevel);

  postLevel(avgLevel, "stats_avg");
  postLevel(maxLevel, "stats_max");
  postLevel(minLevel, "stats_min");
  postLevel(p2pLevel, "stats_p2p");
}