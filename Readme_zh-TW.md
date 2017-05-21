[[English](./Readme.md)]

# 簡介
這個目錄中的程式是針對[KISSlicer](http://www.kisslicer.com/)產生的G-Code開發的，並不適用於其他切片軟體產生的G-Code檔案。要使用本目錄中的程式，你的電腦必需安裝[Python 3.x ](https://www.python.org/downloads/)。

你可以在 KISSlicer 中執行這些程式
> 1. 下載程式到 KISSlicer 目錄中
> 2. 執行 KISSlicer，切換到`Printer`分頁，再切換到`Firmware`子分頁中
> 3. 在`Post-Process`項目中加入命令，例如：`dgm-temp-tower.py -p "<FILE>"`
> ![](./image/post-process.png)
>
> 可利用 & 串連多個命令，例如
> `dgm-heatbed-off.py "<FILE>" 1 & dgm-pause.py -p "<FILE>" 5`
> 表示在 1mm 高的位置關閉熱床，然後在 5mm 高的位置暫停列印


或是在命令列中執行
> `C:\KISSlicer> dgm-temp-tower.py filename.gcode`

# 使用方式
## 一般參數
* `-p，--pause`
  程式結束前，暫停等待使用者按任意鍵。方便在 KISSlicer 中呼叫時，檢視執行過程的訊息。

## Heatbed Off
- 功能: 在指定的層高插入暫停命令
- 使用方式:
	dgm-heatbed-off.py [-p] input-file height
	* **input-file** : 要處理的 gcode 檔
	* **height** : 要關閉熱床的高度

## Pause
- 功能: 在指定的層高插入暫停命令
- 使用方式:
	dgm-pause.py [-p] [-z ZLIFT] [-x X_LOC] [-y Y_LOC] [-c] input-file height [height ...]
	* **input-file** : 要處理的 gcode 檔
	* **height** : 要暫停的高度。若要輸入多個，以空格隔開即可
	* `-z ZLIFT` : 暫停後，擠出頭抬高的距離。預設值為 10.0 mm
	* `-x X_LOC` : 暫停後，X 軸移到指定的位置。未輸入代表不移動。
	* `-y Y_LOC` : 暫停後，Y 軸移到指定的位置。未輸入代表不移動。
	* `-c` : 暫停後，關閉加熱擠出頭。第一次繼續，會重新加熱擠出頭，再暫停。第二次繼續，才開始列印。若列印暫停時人不在列印機旁邊，建議開啟此功能。等人可以操作列印機時再重新加熱。

## Temperature Tower
- 功能: 每隔一個固定高度，插入一個溫度命令。用來做溫度測試。
- 建議模型: [Better Temperature Tower v5 220-180](https://www.thingiverse.com/thing:2222308)
- 使用方式:
	dgm-temp-tower.py [-p] [-zo Z_OFFSET] [-zs Z_STEP] [-to TEMP_OFFSET] [-ts TEMP_STEP] input-file
	* **input-file** : 要處理的 gcode 檔
	* `-zo Z_OFFSET` : 開始插入溫度命令的高度，預設值 1.8 mm
	* `-zs Z_STEP` : 插入溫度命令的高度間隔，預設值 7.0 mm
	* `-to TEMP_OFFSET` : 溫度測試的初始溫度，預設值 220 C
	* `-ts TEMP_STEP` : 溫度測試的溫度間隔，預設值 -5 C
	* 若使用建議的模型，可不用下參數，完全使用預設值即可。
