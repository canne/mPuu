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

global $mPuu;

class mPuuHooks {

	/**
	 * Initialization
	 * @param Parser &$parser
	 * @return true
	 */
     public static function register( Parser &$parser ) {
        // Register the hook with the parser
        $parser->setHook( 'mPuu', [ 'mPuuHooks', 'render' ] );
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
        $mPuu = new mPuu ( $parser );
	    return $mPuu->mPuuRender( $input, $args, $parser );
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
    public static function mPuuArticleSaveHook (&$article, &$user, &$text, &$summary,
                                                $minoredit, $watchthis, $sectionanchor,
                                                &$flags, &$status ) {
        $mPuu = new mPuu ( $parser );
        // Launch some annoyance against the spammers and maybe against the hotheads
        if ( !$mPuu->mPuuSpamFilter( $user, $text ) )
            return false;
        // Find out what would be the Unix file name version of the title
        $thisTitle = $article->getTitle();
        if ( is_null( $thisTitle ) ) {
            $mPuu->mPuuJavaScriptAlert ( 'mPuu_parsernotitle' );
            return 'PARSE_ERROR';
        } // then cannot figure out what is the title of this article
        $filenamebase = $thisTitle->getDBkey();
        if ( $filenamebase == "" ) {
            $mPuu->mPuuJavaScriptAlert ( 'mPuu_parsernofilename' );
            return 'PARSE_ERROR';
        } // then cannot get the file name for this instance
    
        // Set the file paths
        $pathbase    = $$mPuu->mPuuDbDir . '/' . $filenamebase;
        $errFileName = $pathbase . '.err';
    
        // Be optimistic, there will be no errors:
        if ( file_exists ( $errFileName ) )
            unlink ( $errFileName );
    
        // Check and parse the text to find mPuu information and convert it to XML database file
        $parseret = $mPuu->mPuuParsePersonalInformation( $article, $text , $user );
        if ( $parseret == "" )
            return true;
        if ( $parseret == "OK" )
            return true;
        if ( $parseret == "PARSE_ERROR" ) {
            if ( $article->exists () ) {
                $mPuu->mPuuJavaScriptAlert ( 'mPuu_articlenotsaved', "", $errFileName );
                return false;
            } // Then do not allow saving of an existing, failed article
            else {
                $mPuu->mPuuJavaScri1ptAlert ( 'mPuu_newfailednotsaved', "", $errFileName );
                return wfMessage('mPuu_newfailednotsaved2' );;
            } // Else allow saving of a non-yet-existing, failed article
        } // then XML parsing failed
        // Otherwise an internal error (useful for debugging)
        return $parseret;
    
    } // mPuuArticleSaveHook()

} // mPuuHooks class

?>
