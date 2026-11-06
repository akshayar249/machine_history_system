from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
from database import init_db, connect
from config import EXPORT_PATH, PAGE_DIR
app=Flask(__name__); app.secret_key='replace-this-key'; init_db()

@app.route('/')
def index():
    q=request.args.get('q','').strip()
    with connect() as c:
        if q:
            rows=c.execute('SELECT * FROM machines WHERE customer_name LIKE ? OR machine_model LIKE ? OR machine_number LIKE ? ORDER BY id DESC', (f'%{q}%',)*3).fetchall()
        else: rows=c.execute('SELECT * FROM machines ORDER BY id DESC').fetchall()
        mc=c.execute('SELECT COUNT(*) FROM machines').fetchone()[0]
        cc=c.execute('SELECT COUNT(*) FROM components').fetchone()[0]
    return render_template('index.html',machines=rows,q=q,mc=mc,cc=cc)

@app.route('/machine/<int:mid>')
def detail(mid):
    with connect() as c:
        m=c.execute('SELECT * FROM machines WHERE id=?',(mid,)).fetchone()
        if not m:return 'Machine not found',404
        comps=c.execute('SELECT * FROM components WHERE machine_id=? ORDER BY source_page,id',(mid,)).fetchall()
        pages=c.execute('SELECT * FROM page_ocr WHERE machine_id=? ORDER BY page_number',(mid,)).fetchall()
    return render_template('machine.html',m=m,comps=comps,pages=pages)

@app.post('/machine/<int:mid>/save')
def save_machine(mid):
    with connect() as c:
        c.execute('UPDATE machines SET customer_name=?,machine_model=?,machine_number=? WHERE id=?',
                  (request.form.get('customer_name'),request.form.get('machine_model'),request.form.get('machine_number'),mid))
    flash('Machine details saved.'); return redirect(url_for('detail',mid=mid))

@app.post('/component/<int:cid>/save')
def save_component(cid):
    with connect() as c:
        c.execute('UPDATE components SET component_name=?,model=?,make=?,component_type=?,needs_review=0 WHERE id=?',
                  (request.form.get('component_name'),request.form.get('model'),request.form.get('make'),request.form.get('component_type'),cid))
        mid=c.execute('SELECT machine_id FROM components WHERE id=?',(cid,)).fetchone()['machine_id']
    flash('Component saved and marked reviewed.'); return redirect(url_for('detail',mid=mid))

@app.route('/page/<int:mid>/<int:no>')
def page(mid,no):
    with connect() as c: row=c.execute('SELECT page_image FROM page_ocr WHERE machine_id=? AND page_number=?',(mid,no)).fetchone()
    if not row:return 'Page not found',404
    return send_file(PAGE_DIR.parent/row['page_image'])

@app.route('/export')
def export():
    with connect() as c:
        machines=pd.read_sql_query('SELECT * FROM machines',c)
        components=pd.read_sql_query('''SELECT m.customer_name,m.machine_model,m.machine_number,m.source_pdf,
          c.component_name,c.model,c.make,c.component_type,c.source_page,c.needs_review
          FROM components c JOIN machines m ON m.id=c.machine_id ORDER BY m.id,c.source_page,c.id''',c)
    EXPORT_PATH.parent.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(EXPORT_PATH,engine='openpyxl') as w:
        machines.to_excel(w,sheet_name='Machines',index=False); components.to_excel(w,sheet_name='Components',index=False)
    return send_file(EXPORT_PATH,as_attachment=True)

if __name__=='__main__': app.run(debug=True)
