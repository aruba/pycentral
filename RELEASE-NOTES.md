* # 1.1.1

## Notable Changes
* Updated README links

## Known Issues
* No known issues.
  
* # 1.1.0

## Notable Changes
* Added APConfiguration Class to Configuration Module

## Known Issues
* No known issues.
  
* # 1.0.0

## Notable Changes
* Added wait & retry logic when Aruba Central's Per-Second API rate-limit is hit
* Added log messages when Aruba Central's Per-Day API Rate-limit is exhausted
* Added new module for device_inventory APIs
* Added WLAN class to configuration module
* Merged PRs and resolved GitHub issues:
    - PR #16 : Fixing multiple devices to site bug
    - PR #19 : Added ability to associate/unassociate multiple devices to a site
    - PR #20 : Added New Device Inventory Module
    - PR #22 : Added Rate Limit Log Messages
    - PR #23 : Fixed Rate Limit Bugs
    - PR #25 : Licensing API Bug Fixes
    - PR #28, #29 : Added WLAN class to Configuration module

## Known Issues
* No known issues.
  
* # 0.0.3

## Notable Changes
* Quick fix on deprecated pip module usage.
* Merged PRs and resolved GitHub issues:
    - PR #10 : remove dep on _internal function from pip module 
    - Issue #9: pip 21.3 just posted 2 days ago breaks pycentral in the config file and passed to pycentral

## Known Issues
* No known issues.
  
# 0.0.2

## Notable Changes
* Added modules for firmware_management, rapids, topology and user_management
* Major update to existing config_apsettings_from_csv.py workflow. It accepts CSV file downloaded from the Central UI group. This workflow also generates a new CSV file with failed APs. CSV file format from the previous version is not backward compatible.
* Fixes and improvement to existing modules, utilities and the documentation
* Merged PRs and resolved GitHub issues:
    - PR #6: example AP rename code always terminates with an error
    - PR #2: fix url concat in command()
    - PR #1: Added the ability for multiple Aruba Central account's in the config file and passed to pycentral

## Known Issues
* No known issues.

# 0.0.1

## Notable Changes
* This is the initial release for the Aruba Central Python SDK, sample scripts, and workflows.

## Known Issues
* No known issues.
