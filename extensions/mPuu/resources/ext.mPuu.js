/**
 * mPuu is an extension for MediaWiki for simple family tree table
 * building and maintenance.
 *
 * Javascript (this: placeholder for future editing helpers)
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

 ( function ( $, mw ) {
	'use strict';
	mw.hook( 'wikipage.content' ).add( function( $content ) {
        // test hide class "test"
        $(".test").hide();
        }, i;   
    } );
}( jQuery ) );
