import os
import requests
from behave import given, when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions


@when(u'I visit the "home page"')
def step_impl(context):
    #context.resp = requests.get(context.base_url + '/')
    context.driver.get(context.base_url)
    #assert context.resp.status_code == 200


@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in str(context.resp.text)


@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in str(context.resp.text)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()
