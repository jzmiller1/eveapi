Version: 1.4 - 21 February 2015
- Moved package to folder, split one file to speparate files.

Version: 1.3.1 - 02 November 2014
- Fix problem with strings ending in spaces (this is not supposed to happen,
  but apparently tiancity thinks it is ok to bypass constraints)

Version: 1.3.0 - 27 May 2014
- Added set_user_agent() module-level function to set the User-Agent header
  to be used for any requests by the library. If this function is not used,
  a warning will be thrown for every API request.

Version: 1.2.9 - 14 September 2013
- Updated error handling: Raise an AuthenticationError in case
   the API returns HTTP Status Code 403 - Forbidden

Version: 1.2.8 - 9 August 2013
- the XML value cast function (_autocast) can now be changed globally to a
  custom one using the set_cast_func(func) module-level function.

Version: 1.2.7 - 3 September 2012
- Added get() method to Row object.

Version: 1.2.6 - 29 August 2012
- Added finer error handling + added setup.py to allow distributing eveapi
  through pypi.

Version: 1.2.5 - 1 August 2012
- Row objects now have __hasattr__ and __contains__ methods

Version: 1.2.4 - 12 April 2012
- API version of XML response now available as _meta.version

Version: 1.2.3 - 10 April 2012
- fix for tags of the form <tag attr=bla ... />

Version: 1.2.2 - 27 February 2012
- fix for the workaround in 1.2.1.

Version: 1.2.1 - 23 February 2012
- added workaround for row tags missing attributes that were defined
  in their rowset (this should fix ContractItems)

Version: 1.2.0 - 18 February 2012
- fix handling of empty XML tags.
- improved proxy support a bit.

Version: 1.1.9 - 2 September 2011
- added workaround for row tags with attributes that were not defined
  in their rowset (this should fix AssetList)

Version: 1.1.8 - 1 September 2011
- fix for inconsistent columns attribute in rowsets.

Version: 1.1.7 - 1 September 2011
- auth() method updated to work with the new authentication scheme.

Version: 1.1.6 - 27 May 2011
- Now supports composite keys for IndexRowsets.
- Fixed calls not working if a path was specified in the root url.

Version: 1.1.5 - 27 Januari 2011
- Now supports (and defaults to) HTTPS. Non-SSL proxies will still work by
  explicitly specifying http:// in the url.

Version: 1.1.4 - 1 December 2010
- Empty explicit CDATA tags are now properly handled.
- _autocast now receives the name of the variable it's trying to typecast,
  enabling custom/future casting functions to make smarter decisions.

Version: 1.1.3 - 6 November 2010
- Added support for anonymous CDATA inside row tags. This makes the body of
  mails in the rows of char/MailBodies available through the .data attribute.

Version: 1.1.2 - 2 July 2010
- Fixed __str__ on row objects to work properly with unicode strings.

Version: 1.1.1 - 10 Januari 2010
- Fixed bug that causes nested tags to not appear in rows of rowsets created
  from normal Elements. This should fix the corp.MemberSecurity method,
  which now returns all data for members. [jehed]

Version: 1.1.0 - 15 Januari 2009
- Added Select() method to Rowset class. Using it avoids the creation of
  temporary row instances, speeding up iteration considerably.
- Added ParseXML() function, which can be passed arbitrary API XML file or
  string objects.
- Added support for proxy servers. A proxy can be specified globally or
  per api connection instance. [suggestion by graalman]
- Some minor refactoring.
- Fixed deprecation warning when using Python 2.6.

Version: 1.0.7 - 14 November 2008
- Added workaround for rowsets that are missing the (required!) columns
  attribute. If missing, it will use the columns found in the first row.
  Note that this is will still break when expecting columns, if the rowset
  is empty. [Flux/Entity]

Version: 1.0.6 - 18 July 2008
- Enabled expat text buffering to avoid content breaking up. [BigWhale]

Version: 1.0.5 - 03 February 2008
- Added workaround to make broken XML responses (like the "row:name" bug in
  eve/CharacterID) work as intended.
- Bogus datestamps before the epoch in XML responses are now set to 0 to
  avoid breaking certain date/time functions. [Anathema Matou]

Version: 1.0.4 - 23 December 2007
- Changed _autocast() to use timegm() instead of mktime(). [Invisible Hand]
- Fixed missing attributes of elements inside rows. [Elandra Tenari]

Version: 1.0.3 - 13 December 2007
- Fixed keyless columns bugging out the parser (in CorporationSheet for ex.)

Version: 1.0.2 - 12 December 2007
- Fixed parser not working with indented XML.

Version: 1.0.1
- Some micro optimizations

Version: 1.0
- Initial release
