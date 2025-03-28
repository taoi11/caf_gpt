# CAF-GPT File Organization Plan

## Current Issues
- CSS and JS files contain mixed concerns (core functionality + app-specific functionality)
- Some common styles and scripts are duplicated across apps
- No clear separation between core functionality and app-specific code

## Proposed Structure

### Core App
The core app should contain all shared/common elements:

#### Templates
- `core/templates/core/base.html` - Main layout template with common structure
- `core/templates/core/landing_page.html` - Homepage 

#### CSS
##### Old
`core/static/core/css/styles.css`

##### New
- `core/static/core/css/base.css` - Core styles (reset, typography, layout, common components)
- `core/static/core/css/landing_page.css` - Styles specific to the landing page

#### JS
##### Old
- `core/static/core/js/main.js` - Core functionality (menu toggle, tooltips, etc.)
##### New
- `core/static/core/js/base.js` - common functionality 
- `core/static/core/js/landing_page.js` - JS specific to the landing page

### App-Specific Files (pacenote_foo)

#### Templates
- `pacenote_foo/templates/pacenote_foo/pace_notes.html` - App-specific page extending base.html

#### CSS
- `pacenote_foo/static/pacenote_foo/css/pace_notes.css` - Styles specific to the pace notes functionality

#### JS
- `pacenote_foo/static/pacenote_foo/js/pace_notes.js` - JS specific to pace notes functionality
