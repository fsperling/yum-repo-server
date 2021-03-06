#!/bin/bash
_repocomplete() 
{   
    function __getStaticRepos {
       local repos=`curl -f -s "${repohost}:${repoport}/repo.txt"` || local repos=""
       echo $repos
    }

    function __getVirtualRepos {
       local repos=`curl -f -s "${repohost}:${repoport}/repo/virtual.txt"` || local repos=""
       echo $repos
    }

    local repohost repoport cur prev prevprev opts base  username prevprevprev
    username=`whoami`
    if [ -f "/etc/yum-repo-client.yaml" ] #check if defaults file exists
    then
      ###read yaml file.. unfortunately there may be quotes which we need to remove, as well as leading or trailing whitespace
      repohost=`cat "/etc/yum-repo-client.yaml" | grep DEFAULT_HOST | cut -d ":" -f 2 | sed 's/\"//g' | sed "s/\\'//g" | tr -d " "`
      repoport=`cat "/etc/yum-repo-client.yaml" | grep DEFAULT_PORT | cut -d ":" -f 2 | sed 's/\"//g' | sed "s/\\'//g" | tr -d " "`
    else 
      ### no defaults file -> no repo listing completion
      repohost="no_default_set" 
      repoport="80"
    fi

    ### check current autocompletion state
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    [[ "$COMP_CWORD" -gt "1" ]] && prevprev="${COMP_WORDS[COMP_CWORD-2]}"  
    [[ "$COMP_CWORD" -gt "2" ]] && prevprevprev="${COMP_WORDS[COMP_CWORD-3]}"  

    ### commands (options that can be used only once)
    oneshotopts="create uploadto generatemetadata linktostatic linktovirtual deletevirtual deletestatic deleterpm propagate redirectto tag taglist querystatic queryvirtual untag"
    ### options that can appear anywhere
    opts="--hostname=${repohost} --port=${repoport} --username=${username} --message=\"your_message\""


    case "${prevprevprev}" in
      propagate)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
    esac

       

    ### check previous typed word and react accordingly
    case "${prev}" in
       
      @(-)!(-)*) #starts with a - (but only one minus, not two (or more)) -> user input expected, no autocompletion
        return 0
        ;;

      propagate)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;

      untag)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      
      tag)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;

      taglist)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;

      redirectto)
         local matches=$(__getVirtualRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;

      uploadto)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      generatemetadata)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      linktostatic)
         local matches=$(__getVirtualRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      linktovirtual)
         local matches=$(__getVirtualRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      deleterpm)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      deletestatic)
         local matches=$(__getStaticRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      deletevirtual)
         local matches=$(__getVirtualRepos)
         COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
         return 0
         ;;
      create)
         return 0
         ;;
      *.rpm)  ###mass upload mode, autocomplete RPM file names
         local simple=$(echo ${cur}*)
         if [ -d $cur ] && ! [ -z $cur ]
          then
            case $cur in
              */) ;;
              *) local nested=$(echo ${cur}/*);;
            esac      
         fi
         COMPREPLY=( $(compgen -W "${simple} ${nested}" -- ${cur}) )
         return 0
         ;;
      *)  ### go one step further for commands taking two arguments
         case "${prevprev}" in
            tag)
               COMPREPLY="'my_tag'"
               return 0
               ;;
            propagate)
               COMPREPLY="arch/name"
               return 0
               ;;
            uploadto)
               local simple=$(echo ${cur}*) #current path completion
               if [ -d $cur ] && ! [ -z $cur ]
                then
                  case $cur in
                    */) ;;
                    *) local nested=$(echo ${cur}/*);; #if cur is a directory, look inside it
                  esac      
               fi
               COMPREPLY=( $(compgen -W "${simple} ${nested}" -- ${cur}) )
               return 0
               ;;
            untag)
               local matches=$(for x in `curl -fs "${repohost}:${repoport}/repo/${prev}/tags/"`; do echo ${x}; done)
               COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
               return 0
               ;;

            linktovirtual)
               local matches=$(__getVirtualRepos)
               COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
               return 0
               ;;
            linktostatic)
               local matches=$(__getStaticRepos)
               COMPREPLY=( $(compgen -W "${matches}" -- ${cur}) )
               return 0
               ;;
           deleterpm)
               COMPREPLY="arch/name"
               return 0
               ;;
            *)
               ;;
         esac
         ;;
      esac

    #We need an 'extrawurst' for queries because parameter combinations are allowed
    local snd=${COMP_WORDS[1]} #first option given (after 'repoclient')
    if [ "$snd" = "querystatic" ]
    then
      local matches="-name -tag -notag -newer -older"
      COMPREPLY=( $(compgen -W "${matches} ${opts}" -- ${cur}) )
      return 0
    fi
      
    if [ "$snd" = "queryvirtual" ]
    then
      local matches="-name -newer -older -showDestination"
      COMPREPLY=( $(compgen -W "${matches} ${opts}" -- ${cur}) )
      return 0
    fi

   ### autocomplete options or commands if nothing was passed yet
   [[ "$COMP_CWORD" -eq "1" ]] && COMPREPLY=($(compgen -W "${oneshotopts}" -- ${cur})) #complete a command, options should appear only later

   [[ "$COMP_CWORD" -eq "1" ]] || COMPREPLY=($(compgen -W "${opts}" -- ${cur})) #command was given, so autocomplete options
   return 0
}
complete -F _repocomplete repoclient
