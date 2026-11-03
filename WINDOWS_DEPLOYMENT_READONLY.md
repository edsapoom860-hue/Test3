# คู่มือ Windows Network Demo — Read-only

คู่มือนี้สำหรับสาธิต UBE Safety Talk ด้วย **ข้อมูลสมมติเท่านั้น** ไม่ใช่การเปิด Production และไม่มีการยืนยันตัวตน ให้ผู้สอนและ IT อนุญาตเครื่อง เครือข่าย พอร์ต และช่วงเวลาสาธิตก่อนดำเนินการ

**คำสั่ง `0.0.0.0:8501` ด้านล่างรับการเชื่อมต่อบนทุก IPv4 interface ของเครื่อง A** รวมถึง interface อื่นที่อาจเชื่อมต่อเครือข่ายอื่น จึงต้องให้ IT ตรวจการแยกเครือข่ายและจำกัดต้นทางก่อนรัน หากไม่สามารถจำกัดการเข้าถึงได้ ให้หยุดและใช้ localhost ไม่เปิดพอร์ตออก Internet ไม่ทำ port forwarding และไม่เปิดใช้งาน Production โดยไม่ได้รับอนุญาต

Network Demo ในโปรเจกต์นี้อ่าน `network_demo/data/fictional_reports.csv` และแสดง Dashboard กับ History เท่านั้น **ไม่ได้อ่าน SQLite** ฐานข้อมูลตัวอย่างในคู่มือนี้สร้างเพื่อทดลองแยกต่างหาก ไม่ใช่ฐานข้อมูลที่หน้า Network Demo ใช้

## 1. สำรองและจัดชุด Source

1. ก่อนคัดลอก ให้ผู้รับผิดชอบสำรองต้นฉบับตาม `BACKUP_RESTORE_WORKSHOP.md` และตรวจสอบสำเนาตามนโยบายองค์กรโดยไม่เขียนทับต้นฉบับ
2. จัดชุดสำหรับเครื่อง A โดยคัดลอก source ที่จำเป็น: `network_demo/` เฉพาะโค้ดและ `data/fictional_reports.csv`, โฟลเดอร์ `src/` สำหรับ script สร้างฐานข้อมูลตัวอย่าง, `requirements.txt` และ `.streamlit/config.toml` สำหรับธีม ตรวจชุดไฟล์ก่อนส่งทุกครั้ง
3. **ไม่คัดลอก** `.venv`, `.git`, `__pycache__`, `.env`, `secrets.toml`, ไฟล์ credentials หรือคีย์, ฐานข้อมูลเดิม, backup เดิม, `data/reports.csv`, JSONL และ `data/uploads/` ของโปรเจกต์ต้นฉบับ หรือไฟล์ที่ไม่ยืนยันว่าเป็นข้อมูลสมมติ ติดตั้ง environment ใหม่บน A ไม่ใช้ `.venv` ที่คัดลอกมาจากเครื่องอื่น
4. คัดลอกชุดที่ตรวจแล้วด้วยช่องทางที่ IT อนุญาตไปยังโฟลเดอร์ใหม่บนเครื่อง A เช่น `C:\UBE_Workshop\SafetyTalkDemo` และตรวจว่ามี `network_demo\app.py`, `network_demo\service.py`, `network_demo\data\fictional_reports.csv`, `src\import_csv.py` และ `requirements.txt` หลีกเลี่ยงโฟลเดอร์ที่ซิงก์ Cloud หากไม่ได้รับอนุญาต

## 2. สร้าง Python environment บนเครื่อง A

เปิด PowerShell ในโฟลเดอร์ชุด Source บนเครื่อง A ติดตั้ง Python 3.11+ และ packages ผ่านช่องทางที่ IT อนุญาต ขั้นตอน pip อาจต้องใช้เครือข่ายหรือ package repository ที่อนุญาต; ไม่เปิด Internet หรือขอสิทธิ์ Administrator โดยอัตโนมัติ

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

หากเครื่องไม่มี Python launcher, สร้าง `.venv` ไม่ได้ หรือติดตั้ง package ไม่สำเร็จ ให้หยุดและปรึกษา IT อย่าใช้ `pip install` ลง Python ของระบบเพื่อแก้ปัญหาเอง

## 3. สร้าง SQLite ตัวอย่างแยกจากแอป

ใช้เฉพาะ CSV สมมติที่มากับ Network Demo สร้างไฟล์ใหม่บนเครื่อง A คำสั่งนี้ **เขียนฐานข้อมูลตัวอย่าง** จึงต้องทำก่อนเริ่มสาธิต Read-only และไม่ชี้ไปยังฐานข้อมูลหรือ CSV เดิมของผู้ใช้ หากไฟล์ปลายทางมีอยู่แล้ว ให้หยุดและตรวจสอบกับผู้รับผิดชอบ ไม่เขียนทับ

```powershell
if (Test-Path -LiteralPath 'network_demo\data\workshop_demo.sqlite3') { throw 'ฐานข้อมูลปลายทางมีอยู่แล้ว ให้ตรวจสอบก่อน' }
.\.venv\Scripts\python.exe -m src.import_csv --csv network_demo\data\fictional_reports.csv --database network_demo\data\workshop_demo.sqlite3
```

ตรวจผลว่า `source_rows: 4`, `inserted: 4`, `invalid: 0` และ `total: 4` สำหรับไฟล์สมมติชุดปัจจุบัน หากผลต่างไปให้หยุดตรวจ CSV และข้อความผิดพลาดก่อนใช้งาน การนำเข้าข้อมูลซ้ำสามารถข้าม Report ID เดิมและสร้าง backup ของฐานข้อมูลเดิมได้ จึงไม่ควรรันซ้ำโดยไม่ตรวจไฟล์และพื้นที่จัดเก็บ

## 4. ตรวจ Firewall และรันบนเครื่อง A

ขอ IT ตรวจ Network ACL และ effective Firewall rules สำหรับ TCP 8501, interface ของ A, IP ของ B และแหล่งอื่นที่อาจเข้าถึงได้ รวมถึงนโยบาย HTTPS/Authentication ขององค์กร **ห้ามปิด Firewall ทั้งระบบ หรือปิด CORS/XSRF** เพื่อให้เชื่อมต่อได้ การเปลี่ยนกฎใด ๆ ให้ IT ดำเนินการตามกระบวนการที่อนุมัติ

หลังได้รับอนุญาต ให้เปิด PowerShell ในโฟลเดอร์ชุด Source และรัน:

```powershell
$env:NETWORK_READONLY = '1'
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m streamlit run network_demo\app.py --server.address 0.0.0.0 --server.port 8501 --browser.gatherUsageStats false
```

คงหน้าต่างนี้ไว้ระหว่างสาธิต คำสั่งใช้ `network_demo\app.py` ไม่ใช่ `app.py` ของแอปหลัก ค่า command line นี้แทนค่า `127.0.0.1` ใน `.streamlit/config.toml` สำหรับ process นี้เท่านั้น ไม่มีการแก้ไฟล์ config หากพอร์ต 8501 ถูกใช้ ให้หยุดและประสาน IT ไม่เปลี่ยนพอร์ตหรือกฎโดยพลการ

`NETWORK_DEMO.cmd` ที่มีอยู่เป็นอีกวิธีหนึ่งซึ่งจำกัด bind ไปยัง IP ส่วนตัวที่ระบุและใช้พอร์ต 8502 จึงไม่ใช่คำสั่งเดียวกับขั้นตอน `0.0.0.0:8501` นี้ หาก IT อนุมัติให้ใช้เฉพาะ interface เดียว ให้ใช้วิธีที่ IT กำหนด

## 5. หา IP และทดสอบจากเครื่อง B

บนเครื่อง A เปิด PowerShell อีกหน้าต่างแล้วรัน:

```powershell
ipconfig
```

เลือก IPv4 Address ของ interface ที่ IT อนุญาตสำหรับ LAN สาธิต ไม่ใช้ `0.0.0.0` หรือ `127.0.0.1` เป็นปลายทางจากเครื่อง B จากนั้นบนเครื่อง B รัน โดยแทน `<IP_A>` ด้วย IPv4 จริงของเครื่อง A:

```powershell
Test-NetConnection -ComputerName <IP_A> -Port 8501
```

ดูว่า `TcpTestSucceeded` เป็น `True` แล้วเปิด Browser บน B ไปที่ `http://<IP_A>:8501` ตรวจป้าย **NETWORK DEMO · READ-ONLY** และ **NO AUTHENTICATION**, เปิด Dashboard และ History, ทดลองค้นหาและกรอง และตรวจว่าไม่มีปุ่มบันทึก อนุมัติ ปฏิเสธ อัปโหลด ลบ หรือ Admin

หากเชื่อมต่อไม่ได้ ให้ตรวจว่า process ยังรันอยู่, IP ถูก interface และ IT อนุญาตเส้นทาง/พอร์ตแล้ว จากนั้นส่งผล `Test-NetConnection` ให้ IT ตรวจ ห้ามแก้ Firewall หรือปิด CORS/XSRF เอง นอกจากนี้ให้ IT ทดสอบจากต้นทางที่ไม่ได้รับอนุญาตว่าถูกปฏิเสธ

## 6. หยุดสาธิตและข้อจำกัด

กด `Ctrl+C` ในหน้าต่างที่รัน Streamlit บน A แล้วตรวจจาก B อีกครั้งว่าพอร์ตไม่รับการเชื่อมต่อ แจ้ง IT ปิดหรือคืนค่ากฎชั่วคราวตาม change record หากมี และจัดเก็บหรือลบข้อมูลสมมติชั่วคราวตามนโยบายองค์กรโดยผู้รับผิดชอบ

- Demo ใช้ HTTP และไม่มีระบบ Login, SSO หรือ Authentication ทุกคนที่เชื่อมต่อถึงบริการเห็นข้อมูลสมมติชุดเดียวกัน; Demo User Switcher ไม่ใช่ระบบยืนยันตัวตนและไม่มีในหน้า Network Demo
- Read-only จำกัดการทำงานของสำเนาแอปและ service ไม่ใช่การป้องกันผู้มีสิทธิ์แก้ไขไฟล์โดยตรงบนเครื่อง A ให้ IT ตรวจสิทธิ์ไฟล์และบัญชีผู้ใช้
- การใช้ `0.0.0.0` ไม่ได้จำกัดเครือข่ายด้วยตัวเอง ต้องอาศัยการออกแบบเครือข่ายและกฎที่ IT ตรวจและอนุมัติ ไม่เปิด Internet หรือใช้งาน Production โดยไม่ได้รับอนุญาต
- การติดตั้ง package, การสร้างฐานข้อมูลตัวอย่าง และการทดสอบจากเครื่อง A/B ต้องดำเนินการและบันทึกผลจริงในสภาพแวดล้อมที่ได้รับอนุญาต คู่มือนี้ไม่ได้ยืนยันว่าเครื่องหรือเครือข่ายปลายทางผ่านการทดสอบแล้ว
