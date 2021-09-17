#!/bin/bash

outfile="droidprofile.out"
cmd=""

function reg() {
	cmd="find . "$1" | xargs grep \""$2"\""
	echo -e "[ "$cmd" ]"  >> $outfile
	eval $cmd >> $outfile
	echo -e "\n\n" >> $outfile
}

function reg_java() {
	reg "-name \"*.java\"" $1
}

function reg_cs() {
	reg "-name \"*.cs\"" $1
}

function reg_c_cpp() {
reg "-name \"*.cpp\" -o -name \"*.c\"" $1
}

function reg_java_xml() {
	reg "-name \"*.java\" -o -name \"*.xml\"" $1
}

function reg_xml() {
	reg "-name \"*.xml\"" $1
}

function title() {
	echo -e "****** " $1 " ******\n" >> $outfile
}


rm $outfile 2>/dev/null

find . -name "AndroidManifest.xml"  >> $outfile
find . -name "*.mk"  >> $outfile

title "Permission Usage"
reg_xml .*uses-permission.*android:name.*

title "Network Usage"
reg_java .*java\.net.*
reg_java .*android\.net.*
reg_java .*[sS]ocket.*
reg_java .*http.*
reg_c_cpp .*CURL.*
reg_c_cpp .*[sS]ocket.*
reg_cs .*Network.*
reg_cs .*WWW.*

title "Data Usage and Storage"
reg_java .*[pP]references.*
reg_java .*[fF]ile.*
reg_java .*OutputStream.*
reg_java .*InputStream.*
reg_java .*Reader.*
reg_java .*Writer.*
reg_java .*[sS][qQ][lL].*
reg_java .*query.*
reg_java .*Log.*
reg_java .*println.*
reg_java .*[jJ][sS][oO][nN].*
reg_java .*[xX][mM][lL].*
reg_java .*MediaStore.*
reg_java .*saveData.*

reg_c_cpp .*UserDefaults.*
reg_c_cpp .*fopen.*
reg_c_cpp .*fwrite.*
reg_c_cpp .*stream.*
reg_c_cpp .*CCUserDefault.*
reg_c_cpp .*libxml2.*

reg_cs .*System\.IO.*
reg_cs .*PlayerPrefs.*
reg_cs .*saveData.*
reg_cs .*log.*

title "Native code referencing Java"
reg_c_cpp .*FindClass.*
reg_c_cpp .*CallJniMethod.*
reg_cs .*AndroidJavaClass.*

title Unsafe native methods
reg_c_cpp .*strcpy.*
reg_c_cpp .*memcpy.*

title "Application interaction"
reg_java .*[bB]inder.*
reg_java .*serviceinterface.*
reg_java .*getSystemService.*
reg_java .*getExtras.*
reg_java .*startActivity.*
reg_xml .*android:exported.*
reg_cs .*login.*
reg_cs .*Track.*

title Misc
reg_java_xml .*[wW]eb[vV]iew.*
reg_xml .*SECRET_CODE.*
reg_java .*[pP]assword.*
