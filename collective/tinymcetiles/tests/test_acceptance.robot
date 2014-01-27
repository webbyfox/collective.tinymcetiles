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
  page should contain  Dummy tile
  select frame  css=.plonepopup iframe
  element should be visible  css=form#add-tile
  with the label  Dummy tile  select checkbox
  click button  Create
#  page should contain  img
#  element should be visible css=img.mceTile
  click button  Save


# Then

A visitor can view "dummy"
  wait until page contains  dummy
#  Log out
#  Go to  ${PLONE_URL}/a-document
#  Page should contain  Test tile rendered




With the label
    [arguments]     ${title}   ${extra_keyword}   @{list}
    ${for}=  Get Element Attribute  xpath=//label[contains(., "${title}")]@for
    Run Keyword     ${extra_keyword}  id=${for}   @{list}