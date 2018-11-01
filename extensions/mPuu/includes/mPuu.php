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

class mPuu {

    private $mParser;

    public static $mPuuXmlns;
    public static $mPuuSchemaLocation;
    public static $mPuuDbDir;
    public static $mPuuPtDir;
    public static $mPuuPtDirRelURL;
    public static $mPuuCgiBinURL;
    public static $mPuuTownsDir;
    public static $mPuuHousesDir;
    public static $templateWikiName;
    public static $templateDate;
    public static $templateWikiTown;
    public static $templateWikiHouse;
    public static $genderFemale;
    public static $genderMale;
    public static $mPuuSpamDir;
    public static $spamWords;
    public static $blacklistedPersons;

	public function __construct( $parser ) {

        $this->mParser = $parser;
        // ----------------- Configuration -------------------
        /**
         * The below is the XMLSchema namespace and the schema location.
         * If you do not know more about it, point them to the root of your site.
         */
        $this->mPuuXmlns = 'http://www.makijarvi.fi';
        $this->mPuuSchemaLocation = 'http://www.makijarvi.fi';
        /**
         * How the directories are located related to the MediaWiki's
         * installation directory
         */
        $this->mPuuDbDir = '../mPuu/db/pi';
        $this->mPuuPtDir       = "../../mPuu/graphs/pt";
        $this->mPuuPtDirRelURL = "/mPuu/graphs/pt";
        $this->mPuuCgiBinURL   = "http://www.makijarvi.fi/cgi-bin";
        $this->mPuuTownsDir    = "../../mPuu/xhtml/towns";
        $this->mPuuHousesDir   = "../../mPuu/xhtml/houses";

        /**
         * Some values used in the template and that should be changed if the template is edited
         */
        $this->templateWikiName = 'ETUNIMI SUKUNIMI';
        $this->templateDate = 'VVVV-KK-PV';
        $this->templateWikiTown = 'PAIKAN NIMI';
        $this->templateWikiHouse = 'TALON NIMI';
        /**
         * Allowed, single letter abbreviations for the gender input, of course, here is a language dependency
         */
        $this->genderFemale = 'N';
        $this->genderMale   = 'M';
        /**
         * How the directories are located related to the MediaWiki's
         * installation directory
         */
        $this->mPuuSpamDir = "../../mPuu/spam";
        // Spammer's probable keywords
        $this->spamWords =
            array("haista \x76ittu","voi \x76ittu","\x76ittupää","\x70askapää","\x6Byrpä",
                  "\x70illu","\x68intti","\x6Busipää","\x68omo "," \x68omo","\x68uora",
                  "\x6dulkku","\x70erkele","\x73aatana","\x6Aumalauta");
        // These persons do not want their name to be sited (the first one is for testing)
        $this->blacklistedPersons =
            array("\x42ula Zulu");

	} // mPuu() - default constructor

    /** -----------------------------------------------------------------------
     * Renders the mPuu MediaWiki XML-extension:
     * <mPuu [param1=value1]||[param2=value2]></mPuu>
     * @param $input contains 'sometext'
     * @param $params is an assosiative array of param1, param2, ...
     *        action=familytable
     *              class=[father|mother|both] - must give one of these
     *        action=placetable
     *              class=[houses|persons|all] - must give one of these
     *        action=housetable
     *              class=[places|persons|all] - must give one of these
     *        action=showdberror
     *                 Looks for a file db/(articlename).err and renders it contents if exists, otherwise silent
     *                 delete=[false|true] - true will delete the error file after rendering it
     *        Optionally to all actions:
     *                 refresh=[false|true] - true will launch a looong database analysis....
     *                 debug=[false|true] - true will write some debug output on log file and/or pop-up window
     * @param $parser The MediaWiki parser object
     */
    public function mPuuRender ( $input, $params = array(), $parser = null, $frame = false )
    {
        global $wgTitle;
        $fileNameBase = $wgTitle->getDBkey();
        $urlNameBase = $wgTitle->getPartialURL();
        if ( ($fileNameBase == "") || ($urlNameBase == "") ) {
            $this->mPuuJavaScriptAlert ( 'mPuu_parsernofilename' );
            return '';
        } // then cannot get the file name for this instance
        switch ($params["action"]) {
        case "familytable":
            return $this->mPuuRenderFamilyTable( $params, $parser, $this->mPuuPtDir, $this->mPuuPtDirRelURL,
                                          $this->mPuuCgiBinURL, $fileNameBase, $urlNameBase );
        case "placetable":
            return $this->mPuuRenderPlaceTable( $params, $parser, $this->mPuuTownsDir, $fileNameBase );
        case "housetable":
            return $this->mPuuRenderHouseTable( $params, $parser, $this->mPuuHousesDir, $fileNameBase );
        case "showdberror":
            return $this->mPuuRenderDbError ( $params, $parser, $this->mPuuDbDir, $fileNameBase );
        default:
            return htmlspecialchars( wfMessage( 'mPuu_unknownaction', $params["action"]) );
        } // switch
	
    } // mPuuRender()


    /** -----------------------------------------------------------------------
     * This method stores a JavaScript alert dialog's text in an error file
     * using the message from the language document.
     * @param MediaWiki:MPuu_xxx message
     * @param Error file path, file gets overwritten each time
     * @param Optional string (which will be trimmed from whitespace chars)
     */
    public function mPuuJavaScriptAlertSave ( $message, $errFileName, $msgoption = "")
    {
        $errMsg = wfMessage( $message, ($msgoption==""?"":trim ( $msgoption )) );
        if ( $errFileName == "" ) {
            $this->$this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "errFileName=NULL" );
        } // then no reason to continue
        if ( !$errHandle = fopen( $errFileName, "w" ) ) {
            $this->$this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($errFileName)" );
            return;
        } // then cannot open the error file for writing
        if ( fwrite( $errHandle, $errMsg ) === FALSE) {
            $this->$this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fwrite ($errFileName)" );
            return;
        } // then cannot write into the error file
        fclose( $errHandle );
        return;
    } // mPuuJavaScriptAlertSave()

    /** -----------------------------------------------------------------------
     * This method print out a JavaScript alert dialog with the message from
     * the language document.
     * @param MediaWiki:MPuu_xxx message
     * @param Optional string (which will be trimmed from whitespace chars)
     * @param Optional error file, if the file exists, its contents is inserted
     *        before the above message to the alert dialog box.
     */
    public function mPuuJavaScriptAlert ( $message, $msgoption = "", $errFileName = "" )
    {
        $errFileContents = "";
        if ( $errFileName != "" ) {
            if ( !file_exists ( $errFileName ) ) {
                $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($errFileName)" );
                return;
            } // then given a wrog file name
            if ( !$errHandle = fopen( $errFileName, "r" ) ) {
                $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($errFileName)" );
                return;
            } // then cannot open the error file for reading
            if ( filesize ( $errFileName ) > 0 ) {
                $errFileContents = fread ( $errHandle, filesize ( $errFileName ) );
                fclose( $errHandle );
            } // then there is contents to read
        } // then wanted insert a text from an error file
        $errMsg = wfMessage( $message, ($msgoption==""?"":trim ( $msgoption )) );
        $mscript  = '<script type="text/javascript">';
        $mscript .= 'alert("';
        $mscript .= ($errFileContents==""?$errMsg:$errFileContents . '\n\n-----------\n\n' . $errMsg) . '");';
        $mscript .= '</script>';
        print $mscript;
        return;
    } // mPuuJavaScriptAlert()


    /** -----------------------------------------------------------------------
     * Renders the requested family table from the XML-database and returns
     * XHTML tables filled with adequate family information, selected from
     * the personal information XML-data, collected by the above hook-functions.
     * @param $params is an assosiative array of param1, param2, ...
     *        class=[father|mother|all] - Must give of these
     * @param $mPuuPtDir The location of the nightly generated Personal Family Table graphs
     * @param $mPuuPtDirRelURL The same thing, but seen from the server's root, for the client
     * @param $mPuuCgiBinURL Where to find cgi-bin or scgi-bin scripts of the mPuu package
     * @param $fileNameBase The base file name (person name) without extension (database key)
     * @param $urlNameBase What is the URL encoded part of the above person
     */
    private function mPuuRenderFamilyTable( $params, &$parser, $mPuuPtDir, $mPuuPtDirRelURL,
                                    $mPuuCgiBinURL, $fileNameBase, $urlNameBase )
    {
        // Check arguments
        $outputclass = $params["class"];
        if ( ($outputclass != "father") && ($outputclass != "mother") && ($outputclass != "both") )
            return htmlspecialchars( wfMessage( 'mPuu_unknownclass', $params["class"]) );

        $retvalue = "";
        $oTypeArr = array ( 'father', 'mother' );
        foreach ( $oTypeArr as $oType ) {
            if ( ($outputclass == $oType) || ($outputclass == "both") ) {
                $pathbase      = $mPuuPtDir . '/' . $fileNameBase . '_' . $oType;
                $graphFileName = $pathbase . '.png';
                $cmapFileName  = $pathbase . '.map';
                $graphFileURL  = $mPuuPtDirRelURL . '/' . $fileNameBase . '_' . $oType . '.png';
                if ( !file_exists ( $graphFileName ) )
                    return "\n" . '<div class="mpuu-nodata">'
                        . htmlspecialchars ( wfMessage( 'mPuu_nofamilydata' ) ). '</div>';
                $retvalue .= "\n" . '<div class="mpuu-ptgraph-' . $oType . '">';
                $okMap = false;
                if ( (file_exists ( $cmapFileName )) && !(filesize ( $cmapFileName ) == 0) ) {
                    if ( !$cmapHandle = fopen( $cmapFileName, "r" ) ) {
                        $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($cmapFileName)" );
                        return '';
                    } // then cannot open the file for reading
                    $cmapContents = fread ( $cmapHandle, filesize ( $cmapFileName ) );
                    $retvalue .= "\n" . '<map name="map_' . $oType . '">';
                    $retvalue .= "\n" . $cmapContents;
                    $retvalue .= "\n</map>";
                    fclose( $cmapHandle );
                    $okMap = true;
                } // then Ok clickable bitmap file
                $retvalue .= "\n" . '<img src="' . $graphFileURL . '" alt="' . $fileNameBase . '"';
                if ( $okMap )
                    $retvalue .= ' usemap="#map_' . $oType . '" />' . "\n";
                else
                    $retvalue .= ' />' . "\n";
                $retvalue .= "\n" . '<div class="mpuu-printlink"><a href="' . $mPuuCgiBinURL;
                $retvalue .= '/mpuu-makeptpdf.py?name=' . $urlNameBase . '&line=' . $oType;
                $retvalue .= '" title="PDF">' . htmlspecialchars ( wfMessage( 'mPuu_treeprintview' ) );
                $retvalue .= '</a></div>'  . "\n"; // ends the printable view text block
                $retvalue .= '</div>'  . "\n"; // ends the graphics block
            } // then requested output type is matching a possible, generated file type
        } // foreach possible output type

        return $retvalue;
    
    } // mPuuRenderFamilyTable()

    /** -----------------------------------------------------------------------
     * Renders the requested place table (aka. towns) from the XML-database and returns
     * XHTML tables filled with adequate place information. The information
     * is extracted from the personal information XML-data which has been
     * collected by the above hook-functions.
     * @param $params is an assosiative array of param1, param2, ...
     *        class=[houses|persons|all] - Must give of these
     * @param $parser The MediaWiki parser object
     * @param $mPuuTownsDir The location of the build XHTML files to include
     * @param $fileNameBase The base file name (place or town name), without extension
     */
    private function mPuuRenderPlaceTable( $params, &$parser, $mPuuTownsDir, $fileNameBase )
    {
        // Check arguments
        $outputclass = $params["class"];
        if ( ($outputclass != "houses") && ($outputclass != "persons") && ($outputclass != "all") )
            return htmlspecialchars( wfMessage( 'mPuu_unknownclass', $params["class"]) );

        $retvalue = "";
        if ( ($outputclass == "persons") || ($outputclass == "all") ) {
            $filePath = $mPuuTownsDir . '/' . $fileNameBase . '_persons.xhtml';
            if ( file_exists ( $filePath ) ) {
                if ( !$personHandle = fopen( $filePath, "r" ) ) {
                    $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($filePath)" );
                    return '';
                } // then cannot open the file for reading
                $retvalue .= fread ( $personHandle, filesize ( $filePath ) );
                fclose( $personHandle );
            } // Then ok to read the persons filepath
        } // the the persons list is requested
        if ( ($outputclass == "houses") || ($outputclass == "all") ) {
            $filePath = $mPuuTownsDir . '/' . $fileNameBase . '_houses.xhtml';
            if ( file_exists ( $filePath ) ) {
                if ( !$houseHandle = fopen( $filePath, "r" ) ) {
                    $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($filePath)" );
                    return '';
                } // then cannot open the file for reading
                $retvalue .= fread ( $houseHandle, filesize ( $filePath ) );
                fclose( $houseHandle );
            } // Then ok to read the persons filepath
        } // the the persons list is requested

        if ( $retvalue == "" )
            return '<div class="mpuu-nodata">'. htmlspecialchars ( wfMessage( 'mPuu_noplacedata' ) ). '</div>';

        return $retvalue;
    
    } // mPuuRenderPlaceTable()


    /** -----------------------------------------------------------------------
     * Renders the requested house table from the XML-database and returns
     * XHTML tables filled with adequate house information. The information
     * is extracted from the personal information XML-data which has been
     * collected by the above hook-functions.
     * @param $params is an assosiative array of param1, param2, ...
     *        class=[places|persons|all] - Must give of these
     *        optional:
     *             nickname=[house's nickname in the Personal Info Table]
     * @param $parser The MediaWiki parser object
     * @param $mPuuHousesDir The location of the build XHTML files to include
     * @param $fileNameBase The base file name (house name), without extension
     */
    private function mPuuRenderHouseTable( $params, &$parser, $mPuuHousesDir, $fileNameBase )
    {
        // Check arguments
        $outputclass = $params["class"];
        if ( ($outputclass != "places") && ($outputclass != "persons") && ($outputclass != "all") )
            return htmlspecialchars( wfMessage( 'mPuu_unknownclass', $params["class"]) );
        if ( array_key_exists( 'nickname', $params ) ) {
            $nickname = $params["nickname"];
            if ( $nickname != "" ) {
                $fileNameBase = str_replace( ' ', '_', $nickname );
            } // then use the house's nickname instead of the article's database name
        } // then the parameter array contains house's nickname
        $retvalue = "";
        if ( ($outputclass == "places") || ($outputclass == "all") ) {
            $filePath = $mPuuHousesDir . '/' . $fileNameBase . '_towns.xhtml';
            if ( file_exists ( $filePath ) ) {
                if ( !$townHandle = fopen( $filePath, "r" ) ) {
                    $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($filePath)" );
                    return '';
                } // then cannot open the file for reading
                $retvalue .= fread ( $townHandle, filesize ( $filePath ) );
                fclose( $townHandle );
            } // Then ok to read the persons filepath
        } // the the persons list is requested
        if ( ($outputclass == "persons") || ($outputclass == "all") ) {
            $filePath = $mPuuHousesDir . '/' . $fileNameBase . '_persons.xhtml';
            if ( file_exists ( $filePath ) ) {
                if ( !$personHandle = fopen( $filePath, "r" ) ) {
                    $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($filePath)" );
                    return '';
                } // then cannot open the file for reading
                $retvalue .= fread ( $personHandle, filesize ( $filePath ) );
                fclose( $personHandle );
            } // Then ok to read the persons filepath
        } // the the persons list is requested

        if ( $retvalue == "" )
            return '<div class="mpuu-nodata">'. htmlspecialchars ( wfMessage( 'mPuu_nohousedata' ) ). '</div>';

        return $retvalue;
    
    } // mPuuRenderHouseTable()

    /** -----------------------------------------------------------------------
     * Finds out XML database name of the article. If the XML database directory
     * contains an .err file for the article, its contents is rendered. Otherwise
     * a simple link to the XML database file name is rendered.
     * @param $params is an assosiative array of param1, param2, ...
     * @param $parser The MediaWiki parser object
     * @param $mPuuDbDir The location of the XML personal info database
     * @param $fileNameBase The base file name (person name) without extension
     */
    private function mPuuRenderDbError ( $params, &$parser, $mPuuDbDir, $fileNameBase )
    {
        $deleteFile = ($params["delete"]=="true"?true:false);
        $pathbase    = $mPuuDbDir . '/' . $fileNameBase;
        $errFileName = $pathbase . '.err';
        $xmlFileName = $pathbase . '.xml';
        if ( !file_exists ( $errFileName ) ) {
            if ( file_exists ( $xmlFileName ) ) {
                return '<div class="mpuu-xmlfileok"><a href="../' . $xmlFileName . '">xml</a></div>';
            } // Then Ok, the file is there, show a link into it
            $parser->disableCache();
            return '<div class="mpuu-xmlfileerr">' . wfMessage('mPuu_missingxmlfile', $xmlFileName) . '</div>';
        } // then no error file, XML should be OK then
        if ( !$errHandle = fopen( $errFileName, "r" ) ) {
            $this->mPuuJavaScriptAlert ( 'mPuu_parsefilefailed', "fopen ($errFileName)" );
            return '';
        } // then cannot open the file for reading
        if ( filesize ( $errFileName) == 0 ) {
            fclose ( $errHandle );
            if ( $deleteFile )
                unlink ( $errFileName );
            return '';
        } // then empty file
        $errContents = fread ( $errHandle, filesize ( $errFileName ) );
        fclose( $errHandle );
        if ( $deleteFile )
            unlink ( $errFileName );
        $parser->disableCache();
        return '<pre>' . htmlspecialchars ( str_replace ( '\n', "\n", $errContents ) ) . "<\x2Fpre>";
    
    } // mPuuRenderDbError()

} // mPuu class

?>
