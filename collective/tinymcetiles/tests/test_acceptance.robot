*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As an editor I can inset a "DummyTile" in a document
    Given a site owner
      and a new document
     When I insert a "DummyTile" in a document
     Then a visitor can view "dummy"


*** Keywords ***

# Given

A site owner
  Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

A new document
  Enable autologin as  Manager
  Set autologin username  ${SITE_OWNER_NAME}
  Create content  type=Document
  ...  id=a-document  title=A New Document
  Disable autologin

# When

When I insert a "DummyTile" in a document
  Go to  ${PLONE_URL}/a-document/edit
#    Select Frame  pools_to_register_iframe
  element should be visible  css=.mceLayout .mceToolbar
  Click link  css=.mce_plonetiles
  select frame  css=.plonepopup iframe
  select checkbox  css=#form-field-plone-app-texttile
  page should contain  dummy tile


# Then

A visitor can view "dummy"
  Log out
  Go to  ${PLONE_URL}/a-document
  Page should contain  dummy




