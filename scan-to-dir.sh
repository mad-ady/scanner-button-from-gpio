#!/bin/bash


OUTDIR=/media/aldebaran/scanner/
if [ -d "$1" ]; then
	OUTDIR=$1
fi

D=`date +%Y-%m-%d_%H-%M-%S`
file="$OUTDIR/scan-$D.png"
echo "Scanning to $file..."

scanimage --mode Color --resolution 100 -o "$file"

if [ -f "$file" ]; then
	size=`stat --printf="%s" "$file"`
	echo "Scanned $size bytes"
else
	echo "Error while scanning..."
fi

#Needed by Odroid C1's bad USB bus. Cycle USB-OTG port.
echo "Resetting the USB bus..."
/usr/sbin/uhubctl -a cycle -l 2


