# คู่มือสำรองและทดสอบกู้คืน — UBE Safety Talk Workshop

เอกสารนี้สำหรับข้อมูลสมมติในเครื่อง Workshop เท่านั้น ไม่ใช่แผนสำรองข้อมูล Production ไม่มีการตั้งเวลาสำรองหรือส่งข้อมูลไป Cloud / Server อัตโนมัติ ผู้รับผิดชอบต้องเลือกที่เก็บและดำเนินการเอง

## สิ่งที่ต้องสำรอง

| รายการ | ตำแหน่งในโปรเจกต์ | จุดประสงค์ |
|---|---|---|
| ฐานข้อมูลทดลอง SQLite | `data/safety_talk_demo.sqlite3` หากมี หรือไฟล์ฐานข้อมูลทดลองอื่นที่ผู้สอนระบุ | เก็บรายงาน ผู้ใช้จำลอง และประวัติอนุมัติที่อยู่ในฐานข้อมูลนั้น |
| ไฟล์แนบ | `data/uploads/` | เก็บไฟล์หลักฐานที่ชื่ออยู่ใน `evidence_files` |
| รายงานแอปหลัก | `data/reports.csv` | แอปหลักปัจจุบันบันทึกรายงานลง CSV ไม่ใช่ SQLite |
| เจ้าของและประวัติอนุมัติของแอปหลัก | `data/report_owners.jsonl` และ `data/approval_history.jsonl` หากมี | เก็บข้อมูลประกอบ workflow ที่ไม่ได้อยู่ใน CSV |
| ข้อมูลตัวอย่าง | `data/sample_safety_talk.csv` | รักษาข้อมูลตัวอย่างเดิมของ Workshop |

ตรวจสอบตำแหน่งจริงก่อนสำรอง: หน้าทดลอง SQLite ใช้ `data/safety_talk_demo.sqlite3` แต่ script import สามารถรับฐานข้อมูลปลายทางอื่นได้ และไฟล์นั้นอาจยังไม่มีในเครื่อง การ import CSV เข้า SQLite ไม่ได้ย้าย ownership หรือ approval history จาก JSONL โดยอัตโนมัติ จึงต้องสำรอง JSONL แยก ไม่ถือว่า SQLite แทน CSV และ JSONL ได้

## เมื่อไร เก็บที่ไหน และใครรับผิดชอบ

- **เมื่อไร:** ก่อนเริ่ม Workshop, ก่อน import หรือเปลี่ยนข้อมูล และหลังจบรอบที่ต้องเก็บผลงาน ให้ทำหลังหยุดการบันทึกทั้งหมด ทดสอบกู้คืนอย่างน้อยหนึ่งครั้งก่อนพึ่งพาสำเนานั้น
- **ที่ไหน:** ผู้สอนเลือกโฟลเดอร์หรืออุปกรณ์ **ภายในเครื่องที่ไม่ซิงก์ Cloud และไม่ใช่ network share** ซึ่งองค์กรอนุญาต มีพื้นที่เพียงพอ และจำกัดสิทธิ์เข้าถึง หลีกเลี่ยง OneDrive และโฟลเดอร์ที่ซิงก์อัตโนมัติ ตรวจสอบกับ IT หากไม่แน่ใจ ไม่เก็บสำเนาเพียงชุดเดียวบนอุปกรณ์ที่ต้องการป้องกันความเสียหาย โดยให้ IT กำหนดสื่อและระยะเก็บที่เหมาะสม
- **ผู้รับผิดชอบ:** ผู้สอนเป็นผู้สั่งหยุดการเขียน สร้างสำเนา ตรวจผลและบันทึกวันเวลา/ตำแหน่ง; ผู้ดูแลเครื่องหรือ IT ตรวจสิทธิ์ที่เก็บ พื้นที่ นโยบาย การเข้ารหัสและระยะเก็บ; ผู้สอนร่วมกับ IT ทดสอบกู้คืนและบันทึกผล ชื่อผู้รับผิดชอบจริงและวิธีติดต่อให้ระบุก่อนเริ่ม Workshop

## เหตุใดจึงต้องใช้ SQLite backup API

การคัดลอกไฟล์ `.sqlite3` ด้วยตัวคัดลอกไฟล์ขณะที่มีการเขียนอาจได้สำเนาไม่สอดคล้องกัน โดยเฉพาะเมื่อมี WAL หรือ journal ที่เกี่ยวข้อง อย่าคัดลอกเฉพาะไฟล์ฐานข้อมูลที่กำลังใช้งานแล้วถือว่าปลอดภัย ใช้ `sqlite3.Connection.backup()` เพื่อสร้าง snapshot ที่สอดคล้องกันของ SQLite

**API สำรองเฉพาะฐานข้อมูล** ไม่ได้ทำ snapshot แบบอะตอมมิกพร้อมไฟล์แนบ, CSV หรือ JSONL ดังนั้นให้หยุดแอปและทุก process ที่เขียนข้อมูลก่อนสำรองทั้งชุด รวมทั้งหยุด import และงานเบื้องหลัง ตรวจว่าไม่มีผู้ใช้กำลังบันทึก จากนั้นอย่าเริ่มเขียนจนสำรองไฟล์ทั้งหมดเสร็จ หากหยุดผู้เขียนไม่ได้ ให้เลื่อนการสำรองชุดนี้และประสาน IT ไม่ถือว่าไฟล์ที่ได้สัมพันธ์กัน

`src/import_csv.py` มีการใช้ SQLite backup API ก่อน import ลงฐานข้อมูลที่มีอยู่ แต่เป็นการสำรองเฉพาะฐานข้อมูล ไม่ครอบคลุมไฟล์แนบและ CSV และไม่แทนขั้นตอนนี้ ต้องตรวจผลสำรองก่อนนำไปใช้

## วิธีสำรองด้วยตนเองบน Windows

1. หยุด Streamlit และทุก process ที่เขียนข้อมูล รอจนหยุดจริง ตรวจว่าข้อมูลใน `data/` เป็นข้อมูลสมมติเท่านั้น
2. เปิด PowerShell ที่โฟลเดอร์โปรเจกต์ ตรวจและกำหนด `$backupRoot` เป็นโฟลเดอร์ในเครื่องที่ **มีอยู่แล้ว** และไม่ซิงก์ Cloud ตัวอย่างด้านล่างเป็นเพียง path สมมติ อย่าใช้จนตรวจสอบแล้ว สคริปต์สร้างโฟลเดอร์ย่อยชื่อใหม่ ไม่เขียนทับ backup เดิม
3. หากใช้ฐานข้อมูลชื่ออื่น แก้ `$env:WORKSHOP_DB_SOURCE` ให้เป็น path ของฐานข้อมูลทดลองที่ถูกต้อง หากยังไม่มี SQLite ให้เว้นว่างและจดว่าไม่มีฐานข้อมูลในการสำรองรอบนั้น

```powershell
$backupRoot = 'D:\WorkshopBackups' # ตัวอย่าง: เปลี่ยนเป็นที่เก็บ local ที่ได้รับอนุญาต
if (-not (Test-Path -LiteralPath $backupRoot -PathType Container)) { throw 'ไม่พบโฟลเดอร์ปลายทาง' }
$backupDir = Join-Path $backupRoot ('safety-talk-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $backupDir -ErrorAction Stop | Out-Null
$env:WORKSHOP_BACKUP_DIR = $backupDir
$env:WORKSHOP_DB_SOURCE = 'data\safety_talk_demo.sqlite3' # เว้นว่างหากไม่มี SQLite

@'
import os, sqlite3
from contextlib import closing
from pathlib import Path

source_name = os.environ.get('WORKSHOP_DB_SOURCE', '')
if source_name:
    source = Path(source_name).resolve(strict=True)
    if not source.is_file():
        raise ValueError('SQLite source is not a file')
    target = Path(os.environ['WORKSHOP_BACKUP_DIR']) / 'sqlite_snapshot.sqlite3'
    with target.open('xb'):
        pass
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as src:
        with closing(sqlite3.connect(str(target))) as dst:
            src.backup(dst)
            if dst.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise RuntimeError('SQLite backup integrity check failed')
    print('SQLite snapshot created and integrity checked')
else:
    print('No SQLite source selected')
'@ | .\.venv\Scripts\python.exe -
if ($LASTEXITCODE -ne 0) { throw 'สำรอง SQLite ไม่สำเร็จ ห้ามใช้ชุดนี้; ตรวจข้อผิดพลาดก่อนเริ่มใหม่' }

foreach ($name in @('reports.csv', 'report_owners.jsonl', 'approval_history.jsonl', 'sample_safety_talk.csv')) {
    $source = Join-Path 'data' $name
    if (Test-Path -LiteralPath $source -PathType Leaf) {
        Copy-Item -LiteralPath $source -Destination $backupDir -ErrorAction Stop
    } else { Write-Host "ไม่มีไฟล์ $name ในรอบนี้" }
}
if (Test-Path -LiteralPath 'data\uploads' -PathType Container) {
    Copy-Item -LiteralPath 'data\uploads' -Destination (Join-Path $backupDir 'uploads') -Recurse -ErrorAction Stop
} else { Write-Host 'ไม่มีโฟลเดอร์ uploads ในรอบนี้' }
Write-Host "Backup directory: $backupDir"
```

หากขั้นตอนใดล้มเหลว สำเนาอาจไม่ครบหรือมีไฟล์ SQLite บางส่วน **ห้ามนำชุดนั้นไปใช้** ให้บันทึกข้อผิดพลาดและสร้างชุดใหม่หลังแก้สาเหตุ อย่าลบหรือเขียนทับข้อมูลต้นฉบับ ตรวจจำนวนไฟล์และ hash ของไฟล์แนบเทียบต้นฉบับขณะที่ยังหยุดการเขียน และบันทึกรายการไฟล์ที่ไม่มีในรอบนั้น อย่าบันทึกเนื้อหาไฟล์ ชื่อบุคคล หรือ secret ลงในบันทึกผล

## ทดสอบ Restore โดยไม่ทับต้นฉบับ

1. เลือกโฟลเดอร์สำรองที่ขั้นตอนข้างต้นสำเร็จ และสร้างโฟลเดอร์ทดสอบ **ใหม่และว่าง** ในเครื่องที่ได้รับอนุญาต ไม่ใช้ `data/` ปัจจุบัน ไม่ใช้ network share หรือโฟลเดอร์ Cloud
2. คัดลอก `sqlite_snapshot.sqlite3` (ถ้ามี), CSV, JSONL และโฟลเดอร์ `uploads` จาก backup ไปโฟลเดอร์ทดสอบใหม่ ตรวจรายการไฟล์และ SHA-256 ของ CSV, JSONL และไฟล์แนบทุกไฟล์เทียบกับ backup โดยไม่เปิดเนื้อหาจริง หากไม่มี SQLite ให้บันทึกว่าไม่ได้ทดสอบส่วน SQLite
3. ตรวจฐานข้อมูลสำเนาที่กู้คืนด้วย Python โดยปรับ `$env:RESTORED_SQLITE` ให้ชี้ไปยังสำเนาในโฟลเดอร์ทดสอบเท่านั้น คำสั่งเปิดแบบ read-only ไม่สร้างฐานข้อมูลใหม่:

```powershell
$env:RESTORED_SQLITE = 'D:\WorkshopRestoreTest\sqlite_snapshot.sqlite3' # ตัวอย่าง: เปลี่ยนเป็นสำเนาที่กู้คืน
@'
import os, sqlite3
from contextlib import closing
from pathlib import Path

path = Path(os.environ['RESTORED_SQLITE']).resolve(strict=True)
with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
    db.execute('PRAGMA query_only = ON')
    integrity = db.execute('PRAGMA integrity_check').fetchall()
    foreign_keys = db.execute('PRAGMA foreign_key_check').fetchall()
    if integrity != [('ok',)] or foreign_keys:
        raise RuntimeError('Restore verification failed')
    for table in ('reports', 'users_demo', 'approval_history'):
        print(table, db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])
    print('integrity_check: ok; foreign_key_check: ok')
'@ | .\.venv\Scripts\python.exe -
if ($LASTEXITCODE -ne 0) { throw 'ตรวจฐานข้อมูลที่กู้คืนไม่ผ่าน' }
```

4. รันคำสั่งตรวจข้อ 3 อีกครั้งโดยชี้ `RESTORED_SQLITE` ไปยัง `sqlite_snapshot.sqlite3` ในโฟลเดอร์ backup แล้วเปรียบเทียบจำนวนแถวของแต่ละตารางกับสำเนาที่กู้คืน ตรวจด้วยข้อมูลสมมติว่า Report ID / สถานะ / ประวัติที่คาดไว้ยังอยู่ ตรวจว่าแต่ละชื่อใน `evidence_files` มีไฟล์แนบที่ตรงกัน ทั้งใน CSV และ SQLite ตามชุดที่ใช้งาน และ hash ของไฟล์แนบตรงกับ backup ห้ามถือว่าแค่เปิดไฟล์ได้เพียงพอ
5. บันทึกวันเวลา ผู้ทดสอบ ชุด backup ผลตรวจและข้อผิดพลาดโดยไม่บันทึกข้อมูลส่วนบุคคลหรือ secret หากตรวจไม่ผ่าน ให้หยุด ใช้ backup อีกชุดที่ผ่านการตรวจและแจ้ง IT

การนำกลับไปใช้แทนข้อมูลจริงต้องหยุดผู้เขียนทั้งหมด ตรวจสอบ snapshot และได้รับการดำเนินการตามขั้นตอนที่ผู้สอน/IT กำหนด เก็บสำเนาสถานะปัจจุบันไว้ก่อน ห้ามใช้คำสั่งในคู่มือนี้เขียนทับฐานข้อมูลหรือไฟล์แนบเดิมโดยตรง
