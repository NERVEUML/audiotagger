#!/bin/bash
containsElement () {
	local e
	for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
	return 1
}
getoption(){
	option="$1"
	local  __resultvar=$2
	default="$3"
	if [[ -z "$option" ]]; then
		if [[ -z "$default" ]]; then
			showhelp
			exit
		else 
			option="$default"
		fi
	fi
	if [[ "$__resultvar" ]]; then
		eval $__resultvar="'$option'"
	else
		echo "$option"
	fi

}
