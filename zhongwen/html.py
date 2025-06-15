def 取表單數據(html):
    '傳回 form 的名稱值對'
    from lxml import etree
    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)
    
    xpath = '//form'
    
    forms = tree.xpath(xpath)
    if not forms:
        return None
    
    form = forms[-1]
    
    form_info = {
        'action': form.get('action'),
        'method': form.get('method', 'get').upper(),
        'fields': {}
    }
    
    inputs = form.xpath('.//input | .//textarea | .//select')
    for field in inputs:
        name = field.get('name')
        if not name:
            continue
            
        tag = field.tag
        if tag == 'input':
            field_type = field.get('type', 'text').lower()
            if field_type in ['text', 'hidden', 'password', 'email', 'submit']:
                form_info['fields'][name] = field.get('value', '')
            elif field_type in ['checkbox', 'radio']:
                if field.get('checked'):
                    form_info['fields'][name] = field.get('value', 'on')
        elif tag == 'textarea':
            form_info['fields'][name] = field.text or ''
        elif tag == 'select':
            selected = field.xpath('.//option[@selected]')
            if selected:
                form_info['fields'][name] = selected[0].get('value', selected[0].text or '')
            else:
                first_option = field.xpath('.//option[1]')
                if first_option:
                    form_info['fields'][name] = first_option[0].get('value', first_option[0].text or '')
    
    return form_info
