'''
Created on Jan 4, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from __future__ import with_statement
from cms.admin import forms
from cms.forms.fields import PageSelectFormField
from cms.forms.utils import get_site_choices, get_page_choices
from cms.tests.base import CMSTestCase
from cms.tests.util.context_managers import SettingsOverride
from django.contrib.auth.models import User
from django.core.cache import cache

class Mock_PageSelectFormField(PageSelectFormField): 
    def __init__(self, required=False):
        # That's to have a proper mock object, without having to resort
        # to dirtier tricks. We want to test *just* compress here.
        self.required = required
        self.error_messages = {}
        self.error_messages['invalid_page'] = 'Invalid_page'

class FormsTestCase(CMSTestCase):
    def setUp(self):
        cache.clear()
        
    def test_01_get_site_choices(self):
        result = get_site_choices()
        self.assertEquals(result, [])
        
    def test_02_get_page_choices(self):
        result = get_page_choices()
        self.assertEquals(result, [('', '----')])
        
    def test_03_get_site_choices_without_moderator(self):
        with SettingsOverride(CMS_MODERATOR=False):
            result = get_site_choices()
            self.assertEquals(result, [])
            
    def test_04_get_site_choices_without_moderator(self):
        with SettingsOverride(CMS_MODERATOR=False):
            # boilerplate (creating a page)
            user_super = User(username="super", is_staff=True, is_active=True, 
                is_superuser=True)
            user_super.set_password("super")
            user_super.save()
            self.login_user(user_super)
            self.create_page(title="home", user=user_super)
            # The proper test
            result = get_site_choices()
            self.assertEquals(result, [(1,'example.com')])
            
    def test_05_compress_function_raises_when_page_is_none(self):
        raised = False
        try:
            fake_field = Mock_PageSelectFormField(required=True)
            data_list = (0, None) #(site_id, page_id) dsite-id is not used
            fake_field.compress(data_list)
            self.fail('compress function didn\'t raise!')
        except forms.ValidationError:
            raised = True
        self.assertTrue(raised)
        
    def test_06_compress_function_returns_none_when_not_required(self):
        fake_field = Mock_PageSelectFormField(required=False)
        data_list = (0, None) #(site_id, page_id) dsite-id is not used
        result = fake_field.compress(data_list)
        self.assertEquals(result, None)
        
    def test_06_compress_function_returns_none_when_no_data_list(self):
        fake_field = Mock_PageSelectFormField(required=False)
        data_list = None
        result = fake_field.compress(data_list)
        self.assertEquals(result, None)
        
    def test_07_compress_function_gets_a_page_when_one_exists(self):
        # boilerplate (creating a page)
        user_super = User(username="super", is_staff=True, is_active=True, 
                          is_superuser=True)
        user_super.set_password("super")
        user_super.save()
        self.login_user(user_super)
        home_page = self.create_page(title="home", user=user_super)
        # The actual test
        fake_field = Mock_PageSelectFormField()
        data_list = (0, home_page.pk) #(site_id, page_id) dsite-id is not used
        result = fake_field.compress(data_list)
        self.assertEquals(home_page,result)
            