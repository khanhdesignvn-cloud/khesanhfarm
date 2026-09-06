from pathlib import Path
import base64
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'index.html').as_uri()
FIXTURE=ROOT/'tests'/'fixture-design.png'
FIXTURE.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAD0lEQVR4nGP4z8DAwMDAAAANHQEDasKb6QAAAABJRU5ErkJggg=='))

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1280,'height':900})
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto(URL,wait_until='load')

    body=page.locator('body').inner_text()
    assert 'Thanh toán' not in body
    assert 'chuyển khoản' not in body.lower()
    assert page.locator('#dat-hang,#tab-pay,#pay-qr,#phieu-card').count()==0
    assert page.locator('script[src*="html2canvas"],script[src*="jspdf"]').count()==0

    cards=page.locator('.pc-card')
    assert cards.count()==len(page.evaluate('PRODUCTS'))
    assert page.locator('.design-upload-input').count()==cards.count()
    assert page.locator('.design-upload-preview').count()==cards.count()

    first=cards.first
    first.locator('.pc-head').click()
    upload=first.locator('.design-upload-input')
    upload.set_input_files(str(FIXTURE))
    page.wait_for_function("document.querySelector('.pc-card .design-upload-preview').naturalWidth > 0")
    src_before=first.locator('.design-upload-preview').get_attribute('src')
    assert src_before.startswith('data:image/')

    page.reload(wait_until='load')
    first=page.locator('.pc-card').first
    first.locator('.pc-head').click()
    page.wait_for_function("document.querySelector('.pc-card .design-upload-preview').naturalWidth > 0")
    assert first.locator('.design-upload-preview').get_attribute('src').startswith('data:image/')

    first.locator('.design-remove-btn').click()
    assert first.locator('.design-upload-preview').get_attribute('src') in (None,'')
    assert not errors, errors
    card_count=cards.count()
    browser.close()

print({'payment_removed':True,'product_cards':card_count,'upload_persists':True,'remove_works':True})
