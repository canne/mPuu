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

 <?php
if ( function_exists( 'wfLoadExtension' ) ) {
	wfLoadExtension( 'mPuu' );
	// Keep i18n globals so mergeMessageFileList.php doesn't break
	$wgMessagesDirs['mPuu'] = __DIR__ . '/i18n';
	/* wfWarn(
		'Deprecated PHP entry point used for InputBox extension. Please use wfLoadExtension instead, ' .
		'see https://www.mediawiki.org/wiki/Extension_registration for more details.'
	); */
	return;
} else {
	die( 'This version of the mPuu extension requires MediaWiki 1.31 or greater, tested on 1.31.2' );
}
