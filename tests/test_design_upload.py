from pathlib import Path
import base64
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'index.html').as_uri()
FIXTURE_1=ROOT/'tests'/'fixture-design-1.png'
FIXTURE_2=ROOT/'tests'/'fixture-design-2.png'
PIXEL=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAD0lEQVR4nGP4z8DAwMDAAAANHQEDasKb6QAAAABJRU5ErkJggg==')
FIXTURE_1.write_bytes(PIXEL)
FIXTURE_2.write_bytes(PIXEL)

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    context=browser.new_context(viewport={'width':1280,'height':900})
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto(URL,wait_until='load')

    body=page.locator('body').inner_text()
    assert 'Thanh toán' not in body
    assert 'chuyển khoản' not in body.lower()
    assert page.locator('#dat-hang,#tab-pay,#pay-qr,#phieu-card').count()==0

    products=page.evaluate('PRODUCTS')
    cards=page.locator('.pc-card')
    expected_codes=['KSF-CFHT-001','KSF-CFHT-002','KSF-CFPP-001','KSF-CFSG-A01','KSF-CFSG-L01','KSF-CFDS-A01','KSF-CFDS-L01','KSF-TR-001','KSF-TR-002','KSF-DL-001','KSF-DL-002','KSF-TP-001','KSF-TP-002','KSF-TP-003','KSF-TP-004','KSF-TP-005','KSF-TP-006']
    assert cards.count()==17==len(products)
    assert [p['code'] for p in products]==expected_codes
    assert sorted(set(p['category'] for p in products))==['Cà phê','Dược liệu','Thực phẩm','Trà']
    assert page.locator('.filter-tab').all_text_contents()==['Tất cả','Cà phê','Trà','Dược liệu','Thực phẩm']
    assert page.locator('.design-upload-input[multiple]').count()==17
    assert page.locator('.design-gallery').count()==17
    assert page.locator('.publication-content').count()==17
    assert page.locator('.design-file-status').count()==17

    first=cards.first
    first.locator('.pc-head').click()
    first.locator('.design-upload-input').set_input_files([str(FIXTURE_1),str(FIXTURE_2)])
    page.wait_for_function("document.querySelectorAll('#design-gallery-cfht001 .design-thumb').length===2")
    assert first.locator('.design-thumb').count()==2
    assert first.locator('.design-thumb-delete').count()==2
    assert '2 ảnh' in first.locator('.design-count').inner_text()

    page.reload(wait_until='load')
    first=page.locator('.pc-card').first
    first.locator('.pc-head').click()
    page.wait_for_function("document.querySelectorAll('#design-gallery-cfht001 .design-thumb').length===2")

    first.locator('.design-thumb img').first.click()
    assert page.locator('#design-lightbox.open').count()==1
    assert page.locator('#lightbox-counter').inner_text()=='1 / 2'
    page.locator('#lightbox-next').click()
    assert page.locator('#lightbox-counter').inner_text()=='2 / 2'
    page.locator('#lightbox-zoom-in').click()
    assert page.evaluate('lightboxZoom')>1
    page.locator('#lightbox-reset').click()
    assert page.evaluate('lightboxZoom')==1
    page.locator('#lightbox-close').click()
    assert page.locator('#design-lightbox.open').count()==0

    first.locator('.design-thumb-delete').first.click()
    page.wait_for_function("document.querySelectorAll('#design-gallery-cfht001 .design-thumb').length===1")
    assert first.locator('.design-thumb').count()==1
    assert page.locator('#design-gallery-cfht002 .design-thumb').count()==0
    assert not errors, errors
    card_count=page.locator('.pc-card').count()
    browser.close()

print({'products':card_count,'album_upload':True,'album_persists':True,'delete_per_image':True,'slideshow':True,'zoom':True})
