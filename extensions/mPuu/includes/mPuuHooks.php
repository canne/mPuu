<?php

/**
 * mPuu is an extension for MediaWiki for simple family tree table
 * building and maintenance.
 *
 * Usage: wfLoadExtension( 'mPuu' ); in LocalSettings.php
 *
 * This extension version requires MediaWiki 1.31 or higher.
 *
 * The PHP intendation and coding standards are according to PEAR project
 * (X)emacs: php-mode-force-pear, intendation 4 spaces (and no tabs, please)
 *
 * @author Petri Makijarvi <pmakijarvi@users.sourceforge.net>
 * @copyright Petri Makijarvi, France, 2006 - 2018
 * @license This is licensed software, see distribution's LICENSE file
 * @package MediaWikiExtensions
 * @version 2.0.0
 */

class mPuuHooks {

    private $mPuu;

	/**
	 * Initialization
	 * @param Parser &$parser
	 * @return true
	 */
     public static function register( Parser &$parser ) {
        $this-mPuu = new mPuu ( $parser );
        // Register the hook with the parser
        $parser->setHook( 'mPuu', [ 'mPuuBox', 'render' ] );
        return true;
        } // register()

    /**
	 * Render method creates the mPuu object and let it do the rendering
	 * @param string $input
	 * @param array $args
	 * @param Parser $parser
	 * @return string
	 */
    public static function render( $input, $args, Parser $parser ) {
	    return $this->mPuu->mPuuRender( $input, $args );
    } // render method

    /** -----------------------------------------------------------------------
     * This method is declared in .json file to be the hook to the page content
     * save. This is the public method towards the file system DB interfacing
     * private methods.
     * We use it for two purposes: 1) to extract and save the mPuu information
     * on a flat-file XML-database and 2) to filter spam.
     * Success return 'true', otherwise 'false' and the document gets not saved.
     * @param article the WikiPage (object) being saved
     * @param user the User (object) saving the articlw
     * @param text the new article content, as a Content object
     * @param summary the article summary (comment)
     * @param minoredit minor flag
     * @param watchthis watch flag (not used, aka always null)
     * @param sectionanchor section number (not used, aka always null)
     * @param flags see WikiPage::doEditContent documentation for flags' definition
     * @param status Status (object)
     * @return bool Return false to abort saving the page
     */
    public static function mPuuArticleSaveHook (&$article, &$user, &$text, &$summary, $minoredit, $watchthis, $sectionanchor, &$flags, &$status ) {
      // Launch some annoyance against the spammers and maybe against the hotheads
        if ( !$this->mPuuSpamFilter( $user, $text ) )
            return false;
      // Find out what would be the Unix file name version of the title
        $thisTitle = $article->getTitle();
        if ( is_null( $thisTitle ) ) {
            mPuuJavaScriptAlert ( 'mPuu_parsernotitle' );
            return 'PARSE_ERROR';
        } // then cannot figure out what is the title of this article
        $filenamebase = $thisTitle->getDBkey();
        if ( $filenamebase == "" ) {
            mPuuJavaScriptAlert ( 'mPuu_parsernofilename' );
            return 'PARSE_ERROR';
        } // then cannot get the file name for this instance
    
        // Set the file paths
        $pathbase    = $$this->mPuu->mPuuDbDir . '/' . $filenamebase;
        $errFileName = $pathbase . '.err';
    
        // Be optimistic, there will be no errors:
        if ( file_exists ( $errFileName ) )
            unlink ( $errFileName );
    
        // Check and parse the text to find mPuu information and convert it to XML database file
        $parseret = $this->mPuuParsePersonalInformation( $article, $text , $user );
        if ( $parseret == "" )
            return true;
        if ( $parseret == "OK" )
            return true;
        if ( $parseret == "PARSE_ERROR" ) {
            if ( $article->exists () ) {
                mPuuJavaScriptAlert ( 'mPuu_articlenotsaved', "", $errFileName );
                return false;
            } // Then do not allow saving of an existing, failed article
            else {
                mPuuJavaScriptAlert ( 'mPuu_newfailednotsaved', "", $errFileName );
                return wfMsg('mPuu_newfailednotsaved2' );;
            } // Else allow saving of a non-yet-existing, failed article
        } // then XML parsing failed
        // Otherwise an internal error (useful for debugging)
        return $parseret;
    
    } // mPuuArticleSaveHook()

    /** -----------------------------------------------------------------------
     * The mPuu simplified spam-filter and a black-list for names.
     * It is intended to be as countermesure against family black sheep or such;
     * not much of use against a computer literate one, I guess ... :)
     * Well, it is here as first aid kit while one is looking for other solutions!
     * Success return 'true', otherwise 'false' and the document gets not saved.
     * @return bool
     */
    private function mPuuSpamFilter (&$user, &$text) {

        $keywordsfound = false;
        $showSpamWord = '';
        foreach ( $this->mPuu->spamWords as $spamword ) {
            if ( !stristr( $text, $spamword ) === FALSE ) {
                $keywordsfound = true;
                $showSpamWord = $spamword;
                break;
            } // then a spam word found, one is enough to stop saving
        } // for each spamword
        $blacklistedfound = false;
        $showblackListed = '';
        foreach ( $this->mPuu->blacklistedPersons as $blacklisted ) {
            if ( !stristr( $text, $blacklisted ) === FALSE ) {
                $blacklistedfound = true;
                $showblackListed = $blacklisted;
                break;
            } // then a blacklisted person found, one is enough to stop everything
        } // for each item in the black-list
    
        if ( !$keywordsfound && !$blacklistedfound )
            return true;
    
        // Save suspected article text in a file with user's name
        $filename = $this->mPuu->mPuuSpamDir . '/' . $user->getName() . '.txt';
        if ( !$handle = fopen( $filename, "a" ) ) {
            $this->mPuu->mPuuJavaScriptAlert ( 'mPuu_spamsavefailed', "fopen ($filename)" );
        } // then cannot open the file
        else {
            if ( fwrite( $handle, $text . "\n" . '(' . $showSpamWord . ")\n") === FALSE ) {
                $this->mPuu->mPuuJavaScriptAlert ( 'mPuu_spamsavefailed', "fwrite ($filename)" );
            } // then cannot write to the file
            fclose ( $handle );
        } // else able to open the file
    
        if ( $blacklistedfound ) {
             $this->mPuu->mPuuJavaScriptAlert ( 'mPuu_blacklistednosave', $showblackListed );
             return false;
        } // then put a priority on blacklisted persons, show one by one

        $this->mPuu->mPuuJavaScriptAlert ( 'mPuu_spamnosave' );
    
        return false;
    
    } // mPuuSpamFilter()

    /** ----------------------------------------------------------------------
     * Search MPuu personal information template data from the document text.
     * If found, parse it and convert it to MPuuPersonalInfo.xsd (XMLSchema)
     * compliant XML-database entry and save it as a file. An empty string
     * is returned if the document text does not contain personal information
     * data. If the personal information data is found and its parsing
     * is successful the function returns a string 'OK'.
     * 
     * If the parse fails, a string 'PARSE_ERROR' is returned. In this case,
     * an error message is printed out in a JavaScript alert-dialog box.
     * Error messages are language dependent and stored in MediaWiki namespace.
     * The calling function may want to disallow storing of the false data.
     * This way user can iterate the cause of the error until the saving success
     * is obtained.
     *
     * For debugging purposes, in case of a fatal error, an error text may be
     * returned instead of 'PARSE_ERROR'.
     *
     * The output of the function is a Unix named file in the $mPuuDbDir with
     * "title.xml". (where title is parsed from the $title argument).
     * @param title Document's title object
     * @param text Text block to analyze
     * @param user Who is saving
     */
    private function mPuuParsePersonalInformation ( &$article, &$text, &$user ) {

        // ----------------- Code -------------------
        // Quickly find if the document text is for us (note the parsing escape string)
        if ( strstr ( $text, '<!-- MPuu PersonalInfo Start -->' ) === FALSE )
            return 'OK';
        if ( !strstr ( $text, 'mPuu: XML Parser:' ) === FALSE )
            return 'OK';
    
        // Find out what would be the Unix file name version of the title
        $thisTitle = $article->getTitle();
        if ( is_null( $thisTitle ) ) {
            $this->mPuu->mPuuJavaScriptAlert ( 'mPuu_parsernotitle' );
            return 'PARSE_ERROR';
        } // then cannot figure out what is the title of this article
        $filenamebase = $thisTitle->getDBkey();
        if ( $filenamebase == "" ) {
            $this->mPuu->mPuuJavaScriptAlert ( 'mPuu_parsernofilename' );
            return 'PARSE_ERROR';
        } // then cannot get the file name for this instance

        // Check if the person saving this document belongs to Sysop-group
        $mGroups = array();
        $mGroups = $user->getGroups ( );
        $sysopUser = false;
        if ( in_array ( "sysop", $mGroups ) )
            $sysopUser = true;
    
        // Is this a template? If it is, then the sysop-user has right to save template mPuu data but not in XML
        $tmplOk = false; $namespaceXmlStoreAllowed = true; $developmentNamespace = false;
        global $wgExtraNamespaces;
        if ( (($thisTitle->getNamespace() == NS_TEMPLATE) ||
              ($thisTitle->getNamespace() == array_search ( 'mPuu', $wgExtraNamespaces)) ) ) {
            $namespaceXmlStoreAllowed = false; $developmentNamespace = true;
            if ( $sysopUser )
                $tmplOk = true;
        } // then this is a development namespace and the storing of the XML storing is not required

        // Set the file paths
        $pathbase    = $this->mPuu->mPuuDbDir . '/' . $filenamebase;
        $xmlFileName = $pathbase . '.xml';
        $inpFileName = $pathbase . '.inp';
        $errFileName = $pathbase . '.err';

        // File reading line buffer, in case we have to probe for something and the re-analyze
        $sLines = array();
    
        // Be optimistic, there will be no errors:
        if ( file_exists ( $errFileName ) )
            unlink ( $errFileName );
    
        // Save article text into a file for line based parsing
        if ( !$inpHandle = fopen( $inpFileName, "w" ) ) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsefilefailed', $errFileName, trim ("fopen (${inpFileName})") );
            return 'PARSE_ERROR';
        } // then cannot open the file for writing
        if ( fwrite( $inpHandle, $text ) === FALSE) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsefilefailed', $errFileName, trim ("fwrite (${inpFileName})") );
            return 'PARSE_ERROR';
        } // then cannot write into the file
        fclose( $inpHandle );
        if ( !$inpHandle = fopen( $inpFileName, "r" ) ) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsefilefailed', $errFileName, trim ("fopen (${inpFileName})") );
            return 'PARSE_ERROR';
        } // then cannot open the file for writing
    
        // Start line based reading and proceed to the first personalinfo line
        $line = "";
        $tablefound = false;
        while ( !feof ( $inpHandle ) && !$tablefound ) {
            $line = fgets ( $inpHandle );
            if  ( !strstr ( $line, '<!-- MPuu PersonalInfo Start -->' ) === FALSE )
                $tablefound = true;
        } // while not found the marker line and not end of file
        $sLines[0] = $line;
        if ( !$tablefound ) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsernostartmarker',$errFileName );
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // could not find the marker, strange.
    
        // Read the next line, which should start the personalinfo table
        $line = fgets ( $inpHandle );
        if ( (strstr ( $line, 'MPuu Table Start') === FALSE) || (strstr ( $line, 'class=personalinfo') === FALSE) ) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsernostarttable', $errFileName, trim($line) );
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // then this is not personalinfo table
        $sLines[1] = $line;
    
        // Prepare the XML-datafile's header
        $xmlBuffer  = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        $xmlBuffer .= '<personalinfo xmlns="' . $mPuuXmlns . '"' . "\n";
        $xmlBuffer .= 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' . "\n";
        $xmlBuffer .= 'xsi:schemaLocation="' . $mPuuSchemaLocation . "\n";
        $xmlBuffer .= $mPuuSchemaLocation . '/MPuuPersonalInformation.xsd' . '">' . "\n";
    
        // PARENTS
        $probeOnly = true; $mustExist = false; $useFile = false; $noFile = true;
        if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- Parents -->', 'parents',
                                 $mustExist, $useFile, $sLines, $errFileName ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the parents sub-table
        if ( ($fatherName = $this->mPuuProbeData ( $inpHandle, 'LinkItem', '', $templateWikiName, $tmplOk,
                                            $mustExist, $useFile, $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find father's name
        $xmlBuffer .= '<father>' . $fatherName . '</father>' . "\n";
        if ( ($motherName = $this->mPuuProbeData ( $inpHandle, 'LinkItem', '', $templateWikiName, $tmplOk,
                                            $mustExist, $useFile, $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find mother's name
        $xmlBuffer .= '<mother>' . $motherName . '</mother>' . "\n";
        if ( $this->mPuuProbeSubTableEnd ( $inpHandle, 'parents', $mustExist,
                                    $useFile, $sLines, $errFileName  ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not get the end of the parents sub-table

        // GENDER
        if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- Gender -->', 'gender',
                                 $mustExist, $useFile, $sLines, $errFileName ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the gender sub-table
        if ( ($genderX = $this->mPuuProbeData ( $inpHandle, 'PlainItem', '', '', $tmplOk,
                                            $mustExist, $useFile, $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the gender data
        $genderX = strtoupper ( $genderX );
        if ( ($genderX != $genderFemale) && ($genderX != $genderMale) ) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsergendervalue', $errFileName,
                                          trim ($genderX) . '\n(' . $genderFemale . '/' . $genderMale . ')' );
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then the given gender data is not valid
        $xmlBuffer .= '<gender>' . $genderX . '</gender>' . "\n";
        if ( $this->mPuuProbeSubTableEnd ( $inpHandle, 'gender', $mustExist,
                                    $useFile, $sLines, $errFileName  ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not get the end of the parents sub-table
 
        // LIFESPAN
        if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- Lifespan -->', 'lifespan',
                                 $mustExist, $useFile, $sLines, $errFileName ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the lifespan sub-table
        if ( ($birthDate = $this->mPuuProbeData ( $inpHandle, 'PlainItem', '2', $templateDate, $tmplOk,
                                            $mustExist, $useFile, $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the birth date
        if ( $birthDate != '?' ) {
            if ( $birthDate != $templateDate ) {
                if ( !$this->mPuuDateCheck ( $birthDate ) ) {
                    $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parserdatevalue', $errFileName,
                                              trim ($birthDate) . '\n(' . $templateDate . ')' );
                    fclose ( $inpHandle );
                    return 'PARSE_ERROR';
                } // then an error in the date format
            } // Then not a template information format
        } // Then check the given date prior of storing it
        $xmlBuffer .= '<birth>' . $birthDate . '</birth>' . "\n";
        if ( ($deathDate = $this->mPuuProbeData ( $inpHandle, 'PlainItem', '2', $templateDate, $tmplOk,
                                            $mustExist, $useFile, $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the birth date
        if ( ($deathDate != '?') &&  ($deathDate != '-') ) {
            if ( $deathDate != $templateDate ) {
                if ( !$this->mPuuDateCheck ( $deathDate ) ) {
                    $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parserdatevalue', $errFileName,
                                              trim ($deathDate) . '\n(' . $templateDate . ')' );
                    fclose ( $inpHandle );
                    return 'PARSE_ERROR';
                } // then an error in the date format
            } // Then not a template information format
        } // Then check the given date prior of storing it
        $xmlBuffer .= '<death>' . $deathDate . '</death>' . "\n";
        if ( $this->mPuuProbeSubTableEnd ( $inpHandle, 'lifespan', $mustExist,
                                    $useFile, $sLines, $errFileName  ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not get the end of the lifespan sub-table

        // NAME
        if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- Name -->', 'name',
                                 $mustExist, $useFile, $sLines, $errFileName ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not find the name sub-table
        // Read the next line, which should start the personalinfo table
        $nameLineWithTemplate = '{{MPuu LinkItem | linkText={{PAGENAME}}}}';
        $line = fgets ( $inpHandle );
        if ( (strstr ( $line, $nameLineWithTemplate ) === FALSE) ) {
            $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parsernamemismatch', $errFileName,
                                      $nameLineWithTemplate . '\n(' . trim($line) . ')' );
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // then the user has changed the name line's template (name = document name)
        $fullArticleName = $thisTitle->getPrefixedText ( );
        $splitName = explode ( ':', $fullArticleName ); // do not take into account the namespaces here
        $personName = ($splitName[0]==$fullArticleName?$splitName[0]:$splitName[1]);
        $xmlBuffer .= '<name>' . $personName . '</name>' . "\n";
        if ( $this->mPuuProbeSubTableEnd ( $inpHandle, 'name', $mustExist,
                                    $useFile, $sLines, $errFileName  ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // Then did not get the end of the name sub-table


        // SPOUSES
        if ( ($xmlSpouses = $this->mPuuGetXMLSequence ( $inpHandle, 'Spouses', 'Spouse', $templateWikiName,
                                                 'Child', $templateWikiName, $tmplOk,
                                                 $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // then the parsing of the multiple sequence table failed for Spouses
        $xmlBuffer .= $xmlSpouses;

        // PLACES
        if ( ($xmlPlaces = $this->mPuuGetXMLSequence ( $inpHandle, 'Places', 'Town', $templateWikiTown,
                                                 'House', $templateWikiHouse, $tmplOk,
                                                 $sLines, $errFileName ) ) == 'PARSE_ERROR' ) {
            fclose ( $inpHandle );
            return 'PARSE_ERROR';
        } // then the parsing of the multiple sequence table failed for Houses
        $xmlBuffer .= $xmlPlaces;

        // End of the personalinfo
        $xmlBuffer .= "</personalinfo>\n";

        // Ready to (re)write the personal information XML database file
        if ( $namespaceXmlStoreAllowed ) {
            if ( !$outHandle = fopen ( $xmlFileName, "w" ) ) {
                $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parserxmlsavefailed', $errFileName,
                                          trim ("fopen (${xmlFileName})") );
                fclose ( $inpHandle );
                return 'PARSE_ERROR';
            } // then cannot open file
            if ( fwrite ( $outHandle, $xmlBuffer ) === FALSE ) {
                $this->mPuu->mPuuJavaScriptAlertSave ( 'mPuu_parserxmlsavefailed', $errFileName,
                                          trim ("fwrite (${xmlFileName})") );
                fclose ( $inpHandle );
                return 'PARSE_ERROR';
            } // then cannot write to the file
            fclose ( $outHandle );
        } // then this is a valid namespace and the personalinformation data can be stored
    
        // Close all the remaining open paths
        fclose ( $inpHandle );
    
        // Ok return
        return "OK";
    
    } // mPuuParsePersonalInformation()

    /**
     * Tables with 0..infinitive sequences within them are read with this function.
     * The function standardizes the tables, such as Places and Spouses.
     * @param $inpHandle   The input file at the position of the next line to read
     * @param $mType   The master element table type (Places, Spouses, ...)
     * @param $sElem1  Sequence element 1 (ex. Spouse)
     * @param $tplE1   Template element type for element 1
     * @param $sElem2  Sequence element 2 (within the sequence element 1) (ex. Children)
     * @param $tmplE2  Template element type for element 1
     * @param $tplOk   Is it OK to save templates (is this a sysop saving a template)?
     * @param $sLines  Array that will hold the stored lines (here two lines)
     * @param $errFile Relative path to the error file
     */
    private function mPuuGetXMLSequence ( $inpHandle, $mType, $sElem1, $tplE1, $sElem2, $tplE2, $tmplOk, &$sLines, $errFile ) {

        $probeOnly = true; $mustExist = false; $useFile = false; $noFile = true;
        $xmlMType = strtolower ( $mType ); $xmlElem1 = strtolower ( $sElem1 ); $xmlElem2 = strtolower ( $sElem2 ); 
        if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- ' . $mType . ' -->', $xmlMType,
                                 $mustExist, $useFile, $sLines, $errFile ) == 'PARSE_ERROR' ) {
            return 'PARSE_ERROR';
        } // Then did not find the master element sub-table
        $noMore1stElement = false; $nof1stElement = 0; $xml1stElementBuff = ''; $xmlNo1stElemName = false;
        if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- ' . $sElem1 . ' ' . ($nof1stElement + 1) . ' -->',
                                 $xmlElem1, $probeOnly, $useFile, $sLines, $errFile ) == 'PARSE_ERROR' ) {
            $noMore1stElement = true;
        } // Then did not find the first 1st element table; no 1st elements (no 2nd elements, either)
        while ( !$noMore1stElement ) {
            // 1ST ELEMENT
            if ( $nof1stElement > 0 ) {
                if ( mPuuProbeNewLine ( $inpHandle, $probeOnly, $useFile, $sLines, $errFile ) == 'PARSE_ERROR' ) {
                    $noMore1stElement = true;
                    break;
                } // Then did not find a new line command. That normally means: no more 1st elements
                if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- ' . $sElem1 . ' ' . ($nof1stElement + 1) . ' -->',
                                         $xmlElem1, $mustExist, $useFile, $sLines, $errFile ) == 'PARSE_ERROR' ) {
                    return 'PARSE_ERROR';
                } // Then did not find no more sub-tables for 1st elements, although the newline command was there?
            } // Then probe for the new line before the next 1st element table
            if ( ($name1stElement = $this->mPuuProbeData ( $inpHandle, 'LinkItem', '', $tplE1, $tmplOk,
                                                    $mustExist, $useFile, $sLines, $errFile ) ) == 'PARSE_ERROR' ) {
                return 'PARSE_ERROR';
            } // Then did not find first element's name
            if ( $name1stElement == '?' ) {
                $xmlNo1stElemName = true;
            } // then there is a first element name but marked as unknown: cannot save any further information
            else {
                $xml1stElementBuff .= "<${xmlElem1}>\n<${xmlElem1}name>${name1stElement}</${xmlElem1}name>\n";
                $xmlNo1stElemName = false;
            } // else there is (the XML mandatory) first element name that is valid
            $has2ndElements = true; $noMore2ndElements = false; $nof2ndElements = 0; $xml2ndElementsBuff = '';
            if ( $this->mPuuProbeSubTable ( $inpHandle, '<!-- ' . $sElem2 . ' ' . ($nof1stElement + 1) . ' -->',
                                     $xmlElem2, $probeOnly, $useFile, $sLines, $errFile ) == 'PARSE_ERROR' ) {
                $has2ndElements = false; $noMore2ndElements = true;
            } // Then did not find the second element sub-table for this first element item
            while ( !$noMore2ndElements ) {
                if ( ($name2ndElement = $this->mPuuProbeData ( $inpHandle, 'LinkItem', '', $tplE2, $tmplOk,
                                                        $probeOnly, $useFile, $sLines, $errFile ) ) == 'PARSE_ERROR' ) {
                    $noMore2ndElements = true;
                    if ( $this->mPuuProbeSubTableEnd ( $inpHandle, $xmlElem2, $mustExist,
                                                $noFile, $sLines, $errFile  ) == 'PARSE_ERROR' ) {
                        return 'PARSE_ERROR';
                    } // Then did not get the end of the 2nd element sub-table
                    break;
                } // Then did not find the name of the second element
                if ( !$xmlNo1stElemName ) {
                    if ( $name2ndElement != '?' ) {
                        $xml2ndElementsBuff .= "<${xmlElem2}name>${name2ndElement}</${xmlElem2}name>\n";
                    } // then this a known name, not just a question
                } // then there is a valid 1st element name, we can save the second element name
                $nof2ndElements += 1;
            } // while looping in the second elements sub-table
            if ( !$xmlNo1stElemName ) {
                $xml1stElementBuff .= $xml2ndElementsBuff;
                $xml1stElementBuff .= "</${xmlElem1}>\n";
            } // Then there was a first element name in this loop
            if ( $this->mPuuProbeSubTableEnd ( $inpHandle, $xmlElem1, $mustExist,
                                        ($has2ndElements?$useFile:$noFile), $sLines, $errFile ) == 'PARSE_ERROR' ) {
                return 'PARSE_ERROR';
            } // Then did not get the end of the first element sub-table
            $nof1stElement += 1;
        } // while looping in the 1stElement sub-table
        if ( $this->mPuuProbeSubTableEnd ( $inpHandle, $xmlMType, $mustExist,
                                    $noFile, $sLines, $errFile  ) == 'PARSE_ERROR' ) {
            return 'PARSE_ERROR';
        } // Then did not get the end of the master sequence type sub-table

        return $xml1stElementBuff;

    } // mPuuGetXMLSequence()

    /**
     * Probe from the mPuu template table the next sub-table.
     * Returns 'PARSE_ERROR' in case of a failure.
     * Returns 'OK' in case of a success.
     * @param $inpHandle   The input file at the position of the next line to read
     * @param $markerStr   The sub-table's marker (comment) string to search 1st line
     * @param $classStr    The sub-table's expected class string on the 2nd line
     * @param $probeOnly   Not an error if not the requested sub-table, probe silently
     * @param $noFile      Do not read from the file but use below, stored lines
     * @param $sLines      Array that will hold the stored lines (here two lines)
     * @param $errFile     Relative path to the error file
     */
    private function mPuuProbeSubTable ( $inpHandle, $markerStr, $classStr, $probeOnly, $noFile, &$sLines, $errFile ) {

        $lastLine = $this->mPuuGetSetLastLine ( $noFile, $sLines );

        if ( ($line = $this->mPuuGetLine ( $inpHandle, $noFile, $sLines, 0, $errFile, $lastLine )) == 'PARSE_ERROR' )
            return $line;
        if  ( strstr ( $line, $markerStr ) === FALSE ) {
            if ( !$probeOnly )
                mPuuJavaScriptAlertSave ( 'mPuu_parsernomarker',$errFile, $markerStr . '\n(' . trim($line) . ')' );
            return 'PARSE_ERROR';
        } // Then no sub-table marker
        if ( ($line = $this->mPuuGetLine ( $inpHandle, $noFile, $sLines, 1, $errFile, $line )) == 'PARSE_ERROR' )
            return $line;
        if ( (strstr ( $line, 'MPuu SubTable Start') === FALSE) ||
             (strstr ( $line, 'class=' . $classStr ) === FALSE) ) {
            if ( !$probeOnly )
                mPuuJavaScriptAlertSave ( 'mPuu_parsernosubtable', $errFile,
                                          'MPuu SubTable Start | class=' .
                                          $classStr . '\n(' . trim($line) . ')' );
            return 'PARSE_ERROR';
        } // then this is not a valid class for the subtable
        return 'OK';
    } // mPuuProbeSubTable()

    /**
     * Probe from the mPuu template table the next data item.
     * Returns 'PARSE_ERROR' in case of a failure.
     * Returns the data string in case of a success.
     * @param $inpHandle   The input file at the position of the next line to read
     * @param $iType       The mPuu template type you are probing
     * @param $iPos        On which position (the number of '=' signs) data is located if several
     *                     data items given on the line. Possible values ("", "1", "2", "3").
     * @param $tCont       This is the default template contents of the data. Normally its saving would
     *                     be forbidden for the ordinary users, but it is allowed...
     * @param $tmplOk       ... for the system operator saving a templage (because the templates must be saved!)
     * @param $probeOnly   Not an error if not the requested sub-table, probe silently
     * @param $noFile      Do not read from the file but use below, stored lines
     * @param $sLines      Array that will hold the stored lines (here a single line)
     * @param $errFile     Relative path to the error file
     */
    private function mPuuProbeData ( $inpHandle, $iType, $iPos, $tCont, $tmplOk, $probeOnly, $noFile, &$sLines, $errFile ) {

        $lastLine = $this->mPuuGetSetLastLine ( $noFile, $sLines );
        if ( ($line = $this->mPuuGetLine ( $inpHandle, $noFile, $sLines, 0, $errFile, $lastLine )) == 'PARSE_ERROR' )
            return $line;
        if ( strstr ( $line, 'MPuu ' . $iType ) === FALSE ) {
            if ( !$probeOnly )
                mPuuJavaScriptAlertSave ( 'mPuu_parsernodataline', $errFile,
                                          trim ($line) . '\n(' . $iType . ')' );
            return 'PARSE_ERROR';
        } // then this is not requested type of template data
        // Define from where to retrieve the data on the line
        $dataInput = 'plainText';
        if ( $iType == 'LinkItem' )
            $dataInput = 'linkText';
        $dataInput .= $iPos;
        // Reel in the line until the supposed data position
        $dataLine = substr ( $line, strpos ( $line, $dataInput ) );
        if ( ($equalPos = strpos ( $dataLine, '=')) === FALSE ) {
            mPuuJavaScriptAlertSave ( 'mPuu_parsernoequalsign', $errFile, trim($line) );
            return 'PARSE_ERROR';
        } // Then cannot find the equal sign to mark the value start
        if ( ($templateEndPos = strpos ( $dataLine, '|')) === FALSE )
            if ( ($templateEndPos = strpos ( $dataLine, '}}')) === FALSE ) {
                mPuuJavaScriptAlertSave ( 'mPuu_parsernotemplateend', $errFile, trim($line) );
                return 'PARSE_ERROR';
            } // Then cannot find the template end mark to mark the value end
        $dataLine = trim ( substr ( $dataLine, ($equalPos + 1), ($templateEndPos - $equalPos - 1) ) );
        if ( $dataLine == "" ) {
            mPuuJavaScriptAlertSave ( 'mPuu_parsernodatagiven', $errFile, trim($line) );
            return 'PARSE_ERROR';
        } // Then there is no data given
        if ( !$tmplOk && (strlen ($dataLine) > 1) ) {
            if ( !(strstr ( $dataLine, $tCont ) === FALSE) ) {
                mPuuJavaScriptAlertSave ( 'mPuu_parsertemplatevalue', $errFile, trim($line) );
                return 'PARSE_ERROR';
           } // Then the line has not been changed but it is still with template value
        } // Then check the non-sysop users against saving un-modified template data
        return $dataLine;
    } // mPuuProbeData()

    /**
     * Read away the end of a mPuu sub-table. We could just read away the line because
     * it is not important for the data but since it is important for the MediaWiki
     * output, let's check it a little bit.
     * Returns 'PARSE_ERROR' in case of a failure.
     * Returns 'OK' in case of a success.
     * @param $inpHandle   The input file at the position of the next line to read
     * @param $classStr    The sub-table's expected class string on the 2nd line
     * @param $probeOnly   Not an error if not the requested sub-table, probe silently
     * @param $noFile      Do not read from the file but use below, stored lines
     * @param $sLines      Array that will hold the stored lines (here two lines)
     * @param $errFile     Relative path to the error file
     */
    private function mPuuProbeSubTableEnd ( $inpHandle, $classStr, $probeOnly, $noFile, &$sLines, $errFile ) {

        $lastLine = $this->mPuuGetSetLastLine ( $noFile, $sLines );
       if ( ($line = $this->mPuuGetLine ( $inpHandle, $noFile, $sLines, 0, $errFile, $lastLine )) == 'PARSE_ERROR' )
            return $line;
        if ( (strstr ( $line, 'MPuu SubTable End') === FALSE) ||
             (strstr ( $line, 'class=' . $classStr ) === FALSE) ) {
            if ( !$probeOnly )
                mPuuJavaScriptAlertSave ( 'mPuu_parsernosubtableend', $errFile,
                                          'MPuu SubTable End | class=' . $classStr . '\n(' .trim($line) . ')' );
            return 'PARSE_ERROR';
        } // then this is not a valid way to end a mPuu subtable
        return 'OK';
    } // mPuuProbeSubTableEnd()

    /**
     * Probe from the mPuu template table for a new line template command
     * Returns 'PARSE_ERROR' in case of a failure.
     * Returns 'OK' in case of a success.
     * @param $inpHandle   The input file at the position of the next line to read
     * @param $probeOnly   Not an error if not the requested sub-table, probe silently
     * @param $noFile      Do not read from the file but use below, stored lines
     * @param $sLines      Array that will hold the stored lines (here two lines)
     * @param $errFile     Relative path to the error file
     */
    function mPuuProbeNewLine ( $inpHandle, $probeOnly, $noFile, &$sLines, $errFile ) {

        $lastLine = $this->mPuuGetSetLastLine ( $noFile, $sLines );
        if ( ($line = $this->mPuuGetLine ( $inpHandle, $noFile, $sLines, 0, $errFile, $lastLine )) == 'PARSE_ERROR' )
            return $line;
        if  ( strstr ( $line, '<!-- Newline -->' ) === FALSE ) {
            if ( !$probeOnly )
                mPuuJavaScriptAlertSave ( 'mPuu_parsernomarker',$errFile, '<!-- Newline -->\n(' . trim($line) . ')' );
            return 'PARSE_ERROR';
        } // Then no new-line sub-table marker
        if ( ($line = $this->mPuuGetLine ( $inpHandle, $noFile, $sLines, 1, $errFile, $line )) == 'PARSE_ERROR' )
            return $line;
        if ( strstr ( $line, 'MPuu NewLine') === FALSE ) {
            if ( !$probeOnly )
                mPuuJavaScriptAlertSave ( 'mPuu_parsernonewline', $errFile,
                                          'MPuu NewLine\n(' . trim($line) . ')' );
            return 'PARSE_ERROR';
        } // then this is not a template command for a new line
        return 'OK';
    } // mPuuProbeNewLine()

    /**
     * This simple macro is used to shorten up the code of the mPuuProbe...() functions.
     * it is dealing with the stored files array: if the file operation will follow, the
     * array is deleted and then recreated.
     * The return value is the last read line, if available
     * @param $noFile      Do not read from the file but use below, stored lines
     * @param $sLines      Array that will hold the stored lines (here two lines)
     */
    private function mPuuGetSetLastLine ( $noFile, &$sLines ) {
        $lastLine = "";
        if ( !empty($sLines) )
            $lastLine = $sLines[(count($sLines) - 1)];
        if ( !$noFile ) {
            unset ($sLines); $sLines = array();
        } // Then file operations will follow, we can forget the stored lines
        return $lastLine;
    } // mPuuGetSetLastLine()

    /**
     * Read next line from the file, store it to the line buffer array and return it.
     * Or if asked, used only the stored line buffer array and do not touch the file.
     * Returns 'PARSE_ERROR' in case of a failure, otherwise the resulting string.
     * @param $inpHandle   The input file at the position of the next line to read
     * @param $noFile      Do not read from the file but use below, stored lines
     * @param $sLines      Array that will hold the stored lines
     * @param $lineIndex   Actual line index in the stored lines array
     * @param $errFile     Relative path to the error file
     * @param $lastLine    For debugging, what was the last line that we read
     */
    private function mPuuGetLine ( $inpHandle, $noFile, &$sLines, $lineIndex, $errFile, $lastLine ) {
        if ( $noFile ) {
            $line = $sLines[$lineIndex];
        } // Then do not touch the file
        else {
            if ( feof ( $inpHandle ) ) {
                mPuuJavaScriptAlertSave ( 'mPuu_parsereof', $errFile, trim($lastLine) );
                return 'PARSE_ERROR';
            } // Then unexpected end of file
            $line = fgets ( $inpHandle );
            $sLines[$lineIndex] = $line;
        } // else Ok to read from the file
        return $line;
    } // mPuuGetLine()

    /**
    * Checks for a valid date (ISO 8901)
    * This function  is courtesy from the PHP documentation page for checkdate-function
    * http://fr2.php.net/manual/en/function.checkdate.php
    * Many contributors, thanks to all of them. I changed the name to this namespace.
    * @param string  Date in the format given by the format parameter.
    * @param integer Disallow years more than $yearepsilon from now (in future as well as in past)
    * @param string  Formatting string. Has to be one of 'dmy', 'dym', 'mdy', 'myd', 'ydm' or 'ymd'.
    *                (Default is 'ymd' for ISO 8601 compability)
    * @return array [ year, month, day ]
    * @since 1.0
    */

    private function mPuuDateCheck ( $date, $yearepsilon = 5000, $format = 'ymd' ) {
        $date = str_replace ("/", "-", $date);
        $format = strtolower ( $format );
        if ( count ( $datebits = explode ( '-', $date)) != 3 )
            return false;
        $year  = intval ( $datebits[strpos ( $format, 'y' )] );
        $month = intval ( $datebits[strpos ( $format, 'm' )] );
        $day   = intval ( $datebits[strpos ( $format, 'd' )] );
    
        if ( ( abs ( $year - date ('Y') ) > $yearepsilon) || // year outside given range
             ($month < 1) || ($month > 12) || ($day < 1) ||
            (($month == 2) && ($day > 28+(!($year%4))-(!($year%100))+(!($year%400)))) ||
            ($day > 30 + (($month > 7)^($month&1))))
            return false; // date out of range
    
        return array(
                     'year' => $year,
                     'month' => $month,
                     'day' => $day
                     );
    } // mPuuDateCheck()

} // mPuuHooks class

?>
