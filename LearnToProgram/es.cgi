#! /usr/bin/env ruby


#-----------------------------------------------#
#               Learn to Program                #
#                 by Chris Pine                 #
#             Copyright (c) 2003-2009           #
#                 chris@pine.fm                 #
#-----------------------------------------------#


require 'cgi'
require 'stringio'


LINKADDR   = '/LearnToProgram/'
FRLTP_ADDR = 'http://pragmaticprogrammer.com/titles/fr_ltp'


class LearnToProgramTutorial
  @@HLINE = '<div class="fleur"><div class="fleur_stem">&nbsp;</div></div>'
  
  #  If you decide to change coloring or formatting of this tutorial,
  #  you'll want to change these to something appropriate.
  @@NUMBER_COLOR  = 'green'
  @@STRING_COLOR  = 'red'
  @@KEYWORD_COLOR = 'blue'
  @@INPUT_DESC    = 'white box'
  @@OUTPUT_DESC   = 'blue box'
  
  #  Delimiter for input to sample code, since it comes out
  #  right alongside the output.  Must not be html escapable.
  @@INPUT = "%%%'f'o'o'"
  
  
  def initialize (cgi)
    @cgi = cgi
    @depth = 0
    @page  = []
    
    #  'format' is a hidden page for testing formatting.
    @chapters = {'format'=>['Formatting Page',          :generateFormattingPage]}
    @chapters['00'     ] = ['Getting Started',          :generateSetup]
    @chapters['01'     ] = ['Numbers',                  :generateNumbers]
    @chapters['02'     ] = ['Letters',                  :generateLetters]
    @chapters['03'     ] = ['Variables and Assignment', :generateVariables]
    @chapters['04'     ] = ['Mixing It Up',             :generateConversion]
    @chapters['05'     ] = ['More About Methods',       :generateMethods]
    @chapters['06'     ] = ['Flow Control',             :generateFlowControl]
    @chapters['07'     ] = ['Arrays and Iterators',     :generateArrays]
    @chapters['08'     ] = ['Writing Your Own Methods', :generateDefMethod]
    @chapters['09'     ] = ['Classes',                  :generateClasses]
    @chapters['10'     ] = ['Blocks and Procs',         :generateBlocksProcs]
    @chapters['11'     ] = ['Beyond This Tutorial',     :generateBeyond]
  end
  
  def getChapter (method)
    @chapters.each do |num, chapter|
      return num if (method == chapter[1])
    end
    'Main'
  end
  
  def selfLink (chap = nil)
    #  REQUEST_URI includes "?Chapter=Foo"
    LINKADDR+'?Chapter='+(chap ? getChapter(chap) : '')
  end
  
  def makeLink (name, methodName)
    '<a href="'+selfLink(methodName)+'">'+name+'</a>'
  end
  
  def out
    @cgi.out { @page.join("\n")+"\n" }
  end
  
  def puts (string, escapeThis=false)
    if escapeThis
      string = CGI::escapeHTML string
    end
    @page << '  '*@depth+string
  end
  
  def escapeOutputNotInput (output)
    md = /#{@@INPUT}.*?#{@@INPUT.reverse}/.match output
    if md
      CGI::escapeHTML(md.pre_match) +
      CGI::escapeHTML(md[0]).sub(/#{@@INPUT}/,'<span class="L2Pinput">').sub(/#{@@INPUT.reverse}/,'</span>') +
      escapeOutputNotInput(md.post_match)
    else
      CGI::escapeHTML output
    end
  end
  
  def syntaxColor (str)  #  str has probably already been html-escaped.
    lines = str.split /\n/
    #  L2Pcomment
    #  L2Pstring
    #  L2Pnumber
    #  L2Pkeyword
    #  L2Pdefinition
    
    lines.collect! do |line|
      #line += ' '  #  for splitting... Do we need this?
      md = /'|#/.match line
      if md  #  Comment or string.
        syntaxColor(md.pre_match) + 
        if (md[0] == '#')
          '<span class="L2Pcomment">' + md[0] + md.post_match + '</span>'
        else  #  Big string time...
          md2 = /(.*?)(^|[^\\])((\\\\)*)'/.match md.post_match
          if (md2)
            md[0] + '<span class="L2Pstring">' + $1 + $2 + $3 +
                    '</span>' + "'" + syntaxColor(md2.post_match)
          else
            md[0]
          end
        end
      else  #  No comment nor string.
        keywords = %w[__FILE__ and end in or self unless __LINE__
                      begin ensure redo super until BEGIN break do
                      false next rescue then when END case else for
                      nil retry true while alias elsif if not
                      return undef yield]
        
        keywords.each do |keyword|
          line.gsub!(/(\W|^)(#{keyword})(\W|$)/) do
            $1+'<span class="L2Pkeyword">'+$2+'</span>'+$3
          end
        end
        
        ['def', 'class', 'module'].each do |keyword|
          line.gsub!(/(\W|^)(#{keyword}) +([\w?]+)/) do
            $1+'<span class="L2Pkeyword">'   +$2+'</span>'+
              ' <span class="L2Pdefinition">'+$3+'</span>'
          end
        end
        
        line.gsub!(/(^|[-{\[( ^+%*\/?;])(\d+(\.\d+)?|\.\d+)/) do
          $1+'<span class="L2Pnumber">'+$2+'</span>'
        end
        
        line
      end
    end
    
    lines.join "\n"
  end
  
  
  def input (str)
    str = CGI::escapeHTML str
    str.gsub!(/ /, '&nbsp;')
    '<span class="L2Pinput">'+str+'</span>'
  end
  
  def code (str)
    str = CGI::escapeHTML str
    str.gsub!(/ /, '&nbsp;')
    str = syntaxColor  str
    '<span class="L2Pcode">'+str+'</span>'
  end
  
  def output (str)
    str = CGI::escapeHTML str
    str.gsub!(/ /, '&nbsp;')
    '<span class="L2Pcode L2PcodeBG" style="padding-right: 3px; padding-left: 3px;">'+str+'</span>'
  end
  
  #  This is the cool part...
  def executeCode (code, input)
    #  Wrap code to catch errors and to stop SystemExit.
    code = <<-END_CODE
      begin
        #{code}
      rescue SystemExit
      rescue Exception => error
        puts error.inspect
      end
    END_CODE
    
    strIO = StringIO.new
    
    if !input.empty?
      input = input.join("\n")+"\n"
      input = StringIO.new(input, "r")
      class << strIO; self; end.module_eval do
        ['gets', 'getc', 'read'].each do |meth|
          define_method(meth) do |*params|
            inStr = input.method(meth).call(*params)
            puts @@INPUT+inStr.chomp+(@@INPUT.reverse)  #  Echo input.
            inStr
          end
        end
      end
    end
    
    #  Pass these methods to strIO:
    kernelMethods = ['puts', 'putc', 'gets']
    
    #  Swap out Kernel methods...
    kernelMethods.each do |meth|
      Kernel.module_eval "alias __temp__tutorial__#{meth}__ #{meth}"
      Kernel.module_eval do
        define_method(meth) do |*params|
          strIO.method(meth).call(*params)
        end
      end
    end
    
    begin
      strIO.instance_eval code
    rescue Exception => error  #  Catch parse errors.
      return error.inspect
    end
    
    #  ...and swap them back in.
    kernelMethods.each do |meth|
      Kernel.module_eval "alias #{meth} __temp__tutorial__#{meth}__"
    end
    
    strIO.string
  end
  
  
  #  Tags (or similar)
  
  def para (attributes = {}, &block)
    method_missing(:p, attributes, &block)
  end
  
  def prog (execute = [], remark = nil, fakeOutput = nil, &block)
    if !execute
      return progN(&block)
    end
    
    run = {:input => execute}
    run[:remark    ] = remark     if remark
    run[:fakeOutput] = fakeOutput if fakeOutput
    progN(run, &block)
  end
  
  def progN (*trialRuns)
    code = yield
    
    #  Trim leading whitespace.
    lines = code.split $/
    numSpaces = lines[0].length - lines[0].sub(/ */, '').length
    lines.each do |line|
      line.sub!(/ {0,#{numSpaces}}/, '')
    end
    code = lines.join($/)
    
    prettyCode = syntaxColor(CGI::escapeHTML(code))
    
    #  Spit it out.
    puts '<pre class="L2PcodeBlock">'+prettyCode+'</pre>'
    
    trialRuns.each do |run|
      if run[:fakeOutput]
        puts '<pre class="L2PoutputBlock">'+CGI::escapeHTML(run[:fakeOutput])+'</pre>'
      end
      if run[:remark]
        puts '<p>'+run[:remark]+'</p>'
      end
      output = escapeOutputNotInput(executeCode(code,run[:input]))
      puts '<pre class="L2PoutputBlock">'+$/+output+'</pre>'
    end
    nil
  end
  
  #  Makes a tag.
  def method_missing (methodSymbol, attributes = {})
    methodName = methodSymbol.to_s
    
    attribString = ''
    attributes.each do |key, val|
      raise methodName if (key.nil? || val.nil?)
      attribString += ' '+key.to_s+'="'+val+'"'
    end
    if (!block_given?)
      puts '<'+methodName+attribString+' />'
    else
      puts '<'+methodName+attribString+'>'
      @depth += 1
      blockReturn = yield
      puts blockReturn if (blockReturn.kind_of?(String))
      @depth -= 1
      puts '</'+methodName+'>'
    end
    nil
  end
  
  #
  #  TEST PAGE FOR FORMATTING
  #
  
  def generateFormattingPage
    h1 { 'Heading 1' }
    h2 { 'Heading 2' }
    h3 { 'Heading 3' }
    h4 { 'Heading 4' }
    
    para {'Here\'s some code with fake output:'}
    prog [], '...just kidding, dude...', 'FUNKADELIC!' do <<-'END_CODE'
      #  Here is some 'Ruby' code.
      #  5 is better than 6.
      #  def wilma do end if not in, dude.
      #'
      
      '#This shouldn\'t cause any problems.'
      'Neither # should this\\'
      'do end if elsif else case when then while def class'
      'or and not next in'
      'to 3 or not to 3, that is 3.7'
      '' + 'x'+''+''+'..'
               '' +'o'
      
      8
      0.09
      9.9
      5.times {}
      
      puts 'I love cheese.' # yo 'g'
      puts 5.02 + 8 + 0.002  # s'up, muva
      
      jimmy = ['yoyoyo', 66]
      jimmy.each do |item|
        puts item.inspect
      end
      
      puts case 'pumpkin'
        when String then 'yep'
        when Fixnum then 'nope'
        else 'maybe'
      end
      
      def yummy
        if (4 <= 5)
          'Yummm!'
        elsif (4 == 5)
          'Huh?'
        else
          while (1 == 2)
            puts 'What?'
          end
        end
      end
      
      class JustSomeClass
        def initialize
          @var = 5
        end
      end
      
      puts Math::PI  #  Should work.
      puts PI        #  Shouldn't work.
      END_CODE
    end
    para {'Here\'s some code with input and output:'}
    prog ['"Chris"', '&26', '<red>'] do <<-END_CODE
      puts 'yoyo...wuddup?'
      puts 'NAME:'
      name = gets.chomp
      puts 'AGE:'
      age = gets.chomp
      puts 'FAVORITE COLOR'
      color = gets.chomp
      puts 'Hello, '+name+', the '+age+' year-old '+color+' lover.'
      END_CODE
    end
    
    para do <<-END_PARAGRAPH
      Hello there.  I love #{input 'inputting VARIOUS things'}.  I also get a kick
      out of #{code 'coding various things'}.  There's such a thrill in
      seeing all of the exciting #{output 'output you can get'} from a
      well-written program.
      END_PARAGRAPH
    end
  end
  
  #
  #  SETUP
  #
  
  def generateSetup
    para do <<-END_PARAGRAPH
      When you program a computer, you have to "speak" in a
      language your computer understands:  a programming
      language.  There are lots and lots of different
      languages out there, and many of them are excellent.
      In this tutorial I chose to use my favorite
      programming language, <em>Ruby</em>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Aside from being my favorite,
      Ruby is also the easiest programming language I have seen
      (and I've seen quite a few).  In fact, that's the real
      reason I'm writing this tutorial:  I didn't decide to write
      a tutorial, and then choose Ruby because it's my favorite;
      instead, I found Ruby to be so easy that I decided there
      really ought to be a good beginner's tutorial which uses
      it.  It's Ruby's simplicity which prompted this tutorial,
      not the fact that it's my favorite.
      (Writing a similar tutorial using
      another language, like C++ or Java, would have required
      hundreds and hundreds of pages.)  But don't think that
      Ruby is a beginner's language just because it is easy!
      It is a powerful, professional-strength programming
      language if ever there was one.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      When you write something in a human language, what is
      written is called text.  When you write something in a computer
      language, what is written is called <dfn>code</dfn>.  I
      have included lots of examples of Ruby code throughout
      this tutorial, most of them complete programs you can
      run on your own computer.  To make the code easier to
      read, I have colored parts of the code different
      colors.  (For example, numbers are always
      <span class="L2Pcode"><span class="L2Pnumber">#{@@NUMBER_COLOR}</span></span>.)
      Anything you are supposed to type in will be in a
      #{input @@INPUT_DESC}, and anything a program prints
      out will be in a #{output @@OUTPUT_DESC}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      If you come across something you don't understand, or you
      have a question which wasn't answered, write it down and
      keep reading!  It's quite possible that the answer will
      come in a later chapter.  However, if your question was
      not answered by the last chapter, I will tell you where
      you can go to ask it.  There are lots of wonderful people
      out there more than willing to help; you just need to know
      where they are.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      But first we need to download and install Ruby onto your
      computer.
      END_PARAGRAPH
    end
    h2 {'Windows Installation'}
    para do <<-END_PARAGRAPH
      The Windows installation of Ruby is a breeze.  First, you
      need to download the
      <a href="http://rubyinstaller.rubyforge.org/">Ruby installer</a>.
      There might be a couple of versions to choose from; this tutorial
      is using version #{RUBY_VERSION}, so make sure what you download is at
      least as recent as that.  (I would just get the latest
      version available.)  Then simply run the installation program.
      It will ask you where you want to install Ruby.  Unless you have
      a good reason for it, I would just install it in the default
      location.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      In order to program, you need to be able to write programs and
      to run programs.  To do this, you will need a text editor and a
      command line.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      The Ruby installer comes with a lovely text editor called SciTE
      (the Scintilla Text Editor).  You can run SciTE by selecting it
      from the start menu.  If you would like your code to be colored
      like the examples in this tutorial, download these files and
      put them in your SciTE folder (<kbd>c:/ruby/scite</kbd> if you chose the
      default location):
      END_PARAGRAPH
    end
    ul do
      li {'<a href="'+LINKADDR+'SciTEGlobal.properties">Global Properties</a>'}
      li {'<a href="'+LINKADDR+'ruby.properties">Ruby Properties</a>'}
    end
    para do <<-END_PARAGRAPH
      It would also be a good idea to create a folder somewhere to keep
      all of your programs.  Make sure that when you save a program,
      you save it into this folder.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      To get to your command line, select Command Prompt from the
      Accessories folder in your start menu.  You will want to
      navigate to the folder where you are keeping your programs.
      Typing #{input 'cd ..'} will take you up one folder, and
      #{input 'cd foldername'} would put you inside the folder
      named <kbd>foldername</kbd>.  To see all of the folders
      in your current folder, type #{input 'dir /ad'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      And that's it!  You're all set to
      #{makeLink 'learn to program', :generateNumbers}.
      END_PARAGRAPH
    end
    h2 {'Macintosh Installation'}
    para do <<-END_PARAGRAPH
      If you have Mac OS X 10.2 (Jaguar), then you already have
      Ruby on your system!  What could be easier?
      Unfortunately, I don't think you can use Ruby on Mac OS X 10.1 and earlier.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      In order to program, you need to be able to write programs and
      to run programs.  To do this, you will need a text editor and a
      command line.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Your command line is accessible through the Terminal
      application (found in Applications/Utilities).
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      For a text editor, you can use whatever one you are familiar
      or comfortable with.  If you use TextEdit, however, make sure
      you save your programs as text-only!  Otherwise your programs
      <em>will not work</em>.  Other options for programming are
      emacs, vi, and pico, which are all accessible from the
      command line.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      And that's it!  You're all set to
      #{makeLink 'learn to program', :generateNumbers}.
      END_PARAGRAPH
    end
    h2 {'Linux Installation'}
    para do <<-END_PARAGRAPH
      First, you will want to check and see if you have Ruby installed
      already.  Type #{input 'which ruby'}.  If it says something like
      #{output '/usr/bin/which: no ruby in (...)'}, then you need to
      <a href="http://www.ruby-lang.org/en/20020102.html">download Ruby</a>,
      otherwise see what version of Ruby you are running with
      #{input 'ruby -v'}.  If it is older than the latest stable build
      on the above download page, you might want to upgrade.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      If you are the root user, then you probably don't need any
      instructions for installing Ruby.  If you aren't, you might want
      to ask your system administrator to install it for you.  (That way
      everyone on that system could use Ruby.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Otherwise, you can just install it so that only you can use it.
      Move the file you downloaded to a temporary directory, like
      <kbd>$HOME/tmp</kbd>.  If the name of the file is
      <kbd>ruby-1.6.7.tar.gz</kbd>, you can open it with
      #{input 'tar zxvf ruby-1.6.7.tar.gz'}.  Change directory
      to the directory you just created (in this example,
      #{input 'cd ruby-1.6.7'}).
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Configure your installation by typing
      #{input './configure --prefix=$HOME'}).  Next type
      #{input 'make'}, which will build your Ruby interpreter.
      This might take a few minutes.  After that is done, type
      #{input 'make install'} to install it.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Next, you'll want to add <kbd>$HOME/bin</kbd> to your
      command search path by editing your <kbd>$HOME/.bashrc</kbd>
      file.  (You might have to log out and back in again for
      this to take effect.)  After you do that, test your installation:
      #{input 'ruby -v'}.  If that tells you what version of Ruby you
      have, you can now delete the files
      in <kbd>$HOME/tmp</kbd> (or wherever you put them).
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      And that's it!  You're all set to
      #{makeLink 'learn to program', :generateNumbers}.
      END_PARAGRAPH
    end
  end
  
  #
  #  NUMBERS
  #
  
  def generateNumbers
    para do <<-END_PARAGRAPH
      Ahora que tiene todo #{makeLink('instalado', :generateSetup)},
      ¡vamos a escribir un programa! Abra su editor de texto favorito
      y escriba lo siguiente:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 1+2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Guarde su programa (sí, ¡eso es un programa!) como #{input 'calc.rb'}
      (el <strong>.rb</strong> es lo que usualmente ponemos al final de
      los programas escritos con Ruby). Ahora ejecute su programa escribiendo
      #{input 'ruby calc.rb'} en la línea de comandos. Debería obtener un #{output '3'}
      #en su pantalla. ¿Lo ve?, programar no es tan difícil, ¿cierto?
      END_PARAGRAPH
    end
    h2 {'Introducción a '+(code 'puts')}
    para do <<-END_PARAGRAPH
      ¿Cómo es que funciona ese programa? Seguramente puede adivinar qué es lo que
      #{code '1+2'} hace; nuestro programa es básicamente lo mismo que:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 3
      END_CODE
    end
    para do <<-END_PARAGRAPH
      #{code 'puts'} simplemente escribe en la pantalla lo que sea que escribamos a continuación.
      END_PARAGRAPH
    end
    h2 {'Enteros y flotantes'}
    para do <<-END_PARAGRAPH
      En la mayoría de los lenguajes de programación (y Ruby no es la excepción)
      los números sin decimales son llamados <dfn>integers</dfn> (enteros), y
      los números con punto decimal normalmente son llamados
      <dfn>números de punto flotante</dfn>,
      o simplemente, <dfn>floats</dfn>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Aquí hay algunos enteros:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      5
      -205
      9999999999999999999999999
      0
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Y aquí hay algunos flotantes:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      54.321
      0.001
      -205.3884
      0.0
      END_CODE
    end
    para do <<-END_PARAGRAPH
      En la práctica, la mayoría de los programas no usan flotantes; sólo enteros.
      (Después de todo, nadie quiere leer 7,4 emails, o navegar 1,8 páginas,
      o escuchar 5,24 de sus canciones favoritas...)
      Los flotantes se usan más con propósitos académicos (como por ejemplo
      experimentos científicos) y para gráficos en 3D. Incluso la mayoría de los
      programas financieros usan enteros; ¡simplemente llevan un registro de los
      centavos!
      END_PARAGRAPH
    end
    h2 {'Aritmética simple'}
    para do <<-END_PARAGRAPH
      Hasta ahora, tenemos todo lo que necesita una calculadora simple.
      (Las calculadoras siempre usan números de punto flotante, así que si
      quiere que su computadora actúe como una calculadora, también debería
      usar flotantes). Pasa suma y resta, usamos <kbd>+</kbd> y <kbd>-</kbd>,
      como ya lo vimos. Para la multiplicación, usamos <kbd>*</kbd>, y para
      la división usamos <kbd>/</kbd>. La mayoría de los teclados tienen estas
      teclas en el teclado numérico a la derecha. Intentemos expandir un poco
      nuestro programa calc.rb. Escribe lo siguiente y ejecútalo:
      END_PARAGRAPH
    end
    prog [], 'Esto es lo que retorna el programa:' do <<-END_CODE
      puts 1.0 + 2.0
      puts 2.0 * 3.0
      puts 5.0 - 8.0
      puts 9.0 / 2.0
      END_CODE
    end
    para do <<-END_PARAGRAPH
      (Los espacios en el programa no son importantes; simplemente
      hacen que el código sea más fácil de leer). Bueno, eso no
      fue muy sorprendente. Ahora probemos con enteros:
      END_PARAGRAPH
    end
    prog [], 'Básicamente lo misno, ¿no?' do <<-END_CODE
      puts 1+2
      puts 2*3
      puts 5-8
      puts 9/2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Uh... ¡excepto por el último!
      Pero cuando se hace aritmética con enteros, se obtienen enteros.
      Cuando su computadora no puede obtener la respuesta "correcta",
      siempre redondea hacia abajo. (Por supuesto, #{output '4'} <em>es</em>
      la respuesta correcta en aritmética con enteros para #{code '9/2'};
      simplemente tal vez no sea el resultado que esperaba).
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Tal vez se pregunte para qué es útil la división entera. Bueno, digamos
      que va al cine, pero sólo tiene $9. Aquí en Portland, puede ver una
      película en el Bagdad por $2. ¿Cuántas películas puede ver allí?
      #{code '9/2'}... #{output '4'} películas. 4.5 definitivamente <em>no</em>
      es la respuesta correcta en este caso; no le dejarán ver la mitad de
      una película, o dejar que una mitad suya vea la película entera...
      algunas cosas simplemente no son divisibles.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      ¡Así que ahora experimente con algunos programas por su cuenta!
      Si quiere escribir expresiones más complejas, puede usar paréntesis.
      Por ejemplo:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 5 * (12-8) + -15
      puts 98 + (59872 / (13*8)) * -52
      END_CODE
    end
    h2 {'Algunas cosas para intentar'}
    para do
      puts 'Escriba un programa que le diga:'
    end
    ul do
      li {'¿cuántas horas hay en un año?'}
      li {'¿cuántos minutos hay en una década?'}
      li {'¿cuántos segundos de edad tiene usted?'}
      li {'¿cuántos chocolates espera comer en su vida? <br />'+
          '<em><strong>Advertencia:</strong> ¡Esta parte del programa puede tomar tiempo para computarse!</em>'}
    end
    para do
      puts "Aquí hay una pregunta más difícil:"
    end
    ul do
      li {"Si tengo #{(Time.now - Time.mktime(1976,8,3)).to_i / 1000000} millones de segundos de edad, ¿cuántos años tengo?"}
    end
    para do <<-END_PARAGRAPH
      Cuando termine de jugar con números, hechemos un vistazo
      a algunas #{makeLink('letras', :generateLetters)}.
      END_PARAGRAPH
    end
  end
  
  #
  #  LETTERS
  #
  
  def generateLetters
    para do <<-END_PARAGRAPH
      Así que hemos aprendido toco acerca de #{makeLink('números', :generateNumbers)},
      pero qué acerca de letras?  palabras?  texto?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Nos referimos a grupos de letras en un programa como <dfn>cadenas</dfn>.  (Tu puedes
      pensar en letras impresas siendo ensartadas en un cartel.)
      Para que sea más fácil diferencias qué parte del código es una cadena, 
      colorearé las cadenas
      <span class="L2Pcode"><span class="L2Pstring">#{@@STRING_COLOR}</span></span>.
      Aquí hay algunas cadenas:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      'Hola.'
      'Ruby la rompe.'
      '5 es mi número favorito... ¿Cuál es el tuyo?'
      'Snoopy dice #%^?&*@! when he stubs his toe.'
      '     '
      ''
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Como púedes ver, las cadenas pueden tener puntuación, dígitos, símbolos, 
      y espacios dentro... más que solo palabras. Esa última cadena
      no tiene nada; podemos llamarla una cadena <dfn>vacía</dfn>. 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Hemos estado usando #{code 'puts'} para imprimir números;
      intentémoslo con cadenas:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'Hola, mundo!'
      puts ''
      puts 'Adiós.'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Eso funcionó bien. Ahora inténtalo con alguna cadena tuya. 
      END_PARAGRAPH
    end
    h2 {'String Arithmetic'}
    para do <<-END_PARAGRAPH
      Igual que hacer hacer aritmética con números, tu puedes también hacer
      aritmética con cadenas! Bueno, algo así... puedes sumar cadenas, digamos. 
      Intentemos sumar dos cadenas y ver que hace 
      #{code 'puts'} con eso. 
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'Me gusta' + 'el pastel de manzana.'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Whoops!  Me olvidé de poner un espacio entre #{code "'Me gusta'"} y #{code "'el pastel de manzana.'"}.
      Los espacios no importan generalmente, pero si lo hacen dentro de las cadenas. 
      (Es verdad lo que dicen: las computadoras no hacen lo que tu <em>quieres</em>
      que hagan, solo lo que tu <em>le dices</em>  que hagan). Intentémoslo nuevamente:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'Me gusta ' + 'el pastel de manzana.'
      puts 'Me gusta' + ' el pastel de manzana.'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      (Como puedes ver, no importó a qué cadena le agregué el espacio)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Asíq ue puedes sumar cadenas, pero también puedes multiplicarlas!
      (Por un número, es decir) Observa esto:
      END_PARAGRAPH
    end
    prog [], '(Solo bromeaba... realmente hace esto:)', 'pestañeando' do <<-END_CODE
      puts 'parpadeo ' * 4
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Si lo piensas, tiene todo el sentido. Después de todo, 
      #{code '7*3'} realemnte solo significa #{code '7+7+7'}, así que #{code "'moo'*3"} solo
      significa #{code "'moo'+'moo'+'moo'"}.
      END_PARAGRAPH
    end
    h2 {"#{code '12'} vs #{code "'12'"}"}
    para do <<-END_PARAGRAPH
      Antes de ir más allá, debemos asegurarnos de entender la
      diferencia entre <em>números</em> y <em>dígitos</em>.
      #{code '12'} es un número, pero #{code "'12'"} es una cadena de dos dígitos.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Juguemos con esto un poco:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts  12  +  12
      puts '12' + '12'
      puts '12  +  12'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Y qué sucede con esto?:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts  2  *  5
      puts '2' *  5
      puts '2  *  5'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Estos ejemplos fueron bastante directos. De cualquier modo, si no tienes
      cuidado con cómo mezclas tus cadenas y tus números podrías encontrarte con...
      END_PARAGRAPH
    end
    h2 {'Problemas'}
    para do <<-END_PARAGRAPH
      En este punto podrías haber probado algunas cosas que
      <em>no funcionaron</em>. Si no lo haz hecho, aquí hay algunas:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts '12' + 12
      puts '2' * '5'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Hmmm... un mensaje de error.  El problema es eque en realidad
      no puedes sumar un número a una cadena, o multiplicar 
      una cadena por otra cadena. No tiene más sentido que esto:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 'Betty' + 12
      puts 'Fred' * 'John'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Algo más para tener cuidado: Puedes escribir #{code "'pig'*5"} en un programa,
      dado que sólo siognifica #{code '5'} conjuntos de la cadena #{code "'pig'"} todo 
      sumado. De cualquier modo, 
      tu <em>no puedes</em> escribir #{code "5*'pig'"}, ya que eso significa #{code "'pig'"}
      conjuntos de el número #{code '5'}, lo cual es simplemente tonto.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Finalmente, y si quisieras que tu programa imprimiera
      #{output 'You\'re swell!'}?  Podrías intentar:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 'You're swell!'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Bueno, <em>eso</em> no funcionará; No intentaré ni ejecutarlo.
      La computadora pensó que habíamos terminado con la cadena. 
      (Esta es la razón de porque es lindo tener un editor de 
      texto que haga <dfn>coloreo sintáctico</dfn> por ti.)
      ¿Entonces cómo permitimos que la computadora sepa que
      queremos permanecer en la cadena? Tenemos que <dfn>escapar</dfn>
      el apostrofe, de esta manera:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'You\\'re swell!'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      La barra invertida es le caracter de escape. En otras palabras, 
      si tu tienes una barra invertida y otro caracter, ellos a veces son
      convertidos a otro caracter. Las únicas cosas que una barra invertida
      escapa son los apostrofes y las propias barras invertidas. (Si lo 
      piensas un poco, los caracteres escapadas siempre se escapan a sí mismo).
      Unos pocos ejemplos vendrían muy bien, me parece:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'You\\'re swell!'
      puts 'barra invertida al final de la cadena:  \\\\'
      puts 'arriba\\\\abajo'
      puts 'arriba\\abajo'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Dado que la barra invertida <em>no</em> escapa un #{code "'d'"},
      pero <em>si</em> si se escapa a si misma, esos dos últimos caracteres
      son idénticos. No parecen lo mismo en el código, pero en tu computadora
      son realmente los mismos. 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Si tienes alguna pregunta, solo 
      If you have any other questions, just
      #{makeLink('sigue leyendo', :generateVariables)}!  No podría 
      contestar cada pregunta en <em>esta</em> página, después de todo.
      END_PARAGRAPH
    end
  end
  
  #
  #  VARIABLES
  #
  
  def generateVariables
    para do <<-END_PARAGRAPH
      So far, whenever we have #{code 'puts'}ed a string or a number, the thing
      we #{code 'puts'}ed is gone.  What I mean is, if we wanted to print
      something out twice, we would have to type it in twice:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts '...you can say that again...'
      puts '...you can say that again...'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      It would be nice if we could just type it in once and then hang on to it...
      store it somewhere.
      Well, we can, of course&mdash;otherwise, I wouldn't have brought it up!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      To store the string in your computer's memory, we need to
      give the string a name.  Programmers often refer to this process
      as <dfn>assignment</dfn>,
      and they call the names <dfn>variables</dfn>.  This variable can be just
      about any sequence of letters and numbers, but the first character
      needs to be a lowercase letter.  Let's try that last program again,
      but this time I will give the string the name #{code 'myString'} (though I could
      just as well have named it #{code 'str'} or
      #{code 'myOwnLittleString'} or #{code 'henryTheEighth'}).
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      myString = '...you can say that again...'
      puts myString
      puts myString
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Whenever you tried to do something to #{code 'myString'}, the program did it
      to #{code "'...you can say that again...'"} instead.  You can think of the
      variable #{code 'myString'} as "pointing to" the string
      #{code "'...you can say that again...'"}.  Here's a slightly more interesting example:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      name = 'Patricia Rosanna Jessica Mildred Oppenheimer'
      puts 'My name is ' + name + '.'
      puts 'Wow!  ' + name + ' is a really long name!'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Also, just as we can <em>assign</em> an object to a variable,
      we can <em>reassign</em> a different object to that variable.
      (This is why we call them variables:  because what they
      point to can vary.)
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      composer = 'Mozart'
      puts composer + ' was "da bomb", in his day.'
      
      composer = 'Beethoven'
      puts 'But I prefer ' + composer + ', personally.'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Of course, variables can point to any kind of object, not just strings:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      var = 'just another ' + 'string'
      puts var
      
      var = 5 * (1+2)
      puts var
      END_CODE
    end
    para do <<-END_PARAGRAPH
      In fact, variables can point to just about anything...
      except other variables.
      So what happens if we try?
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      var1 = 8
      var2 = var1
      puts var1
      puts var2
      
      puts ''
      
      var1 = 'eight'
      puts var1
      puts var2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      So first, when we tried to point #{code 'var2'} to #{code 'var1'}, it really
      pointed to #{code '8'} instead (just like #{code 'var1'}
      was pointing to).  Then we had #{code 'var1'} point to
      #{code "'eight'"}, but since #{code 'var2'} was never really
      pointing at #{code 'var1'}, it stays pointing at #{code '8'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So now that we've got variables, numbers, and strings, let's learn how to
      #{makeLink 'mix them all up', :generateConversion}!
      END_PARAGRAPH
    end
  end
  
  #
  #  CONVERSION
  #
  
  def generateConversion
    para do <<-END_PARAGRAPH
      We've looked at a few different kinds of objects
      (#{makeLink 'numbers', :generateNumbers} and #{makeLink 'letters', :generateLetters}),
      and we made #{makeLink 'variables', :generateVariables} to point to them;
      the next thing we want to do is to get them all to play nicely together.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      We've seen that if we want a program to print #{output '25'}, the following
      <em>does <strong>not</strong></em> work, because you can't add
      numbers and strings:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      var1 = 2
      var2 = '5'
      
      puts var1 + var2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Part of the problem is that your computer doesn't know if you
      were trying to get #{output '7'} (#{code '2 + 5'}), or if you wanted
      to get #{output '25'} (#{code "'2' + '5'"}).
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Before we can add these together, we need some way of getting the
      string version of #{code 'var1'}, or to get the integer version
      of #{code 'var2'}.
      END_PARAGRAPH
    end
    h2 {'Conversions'}
    para do <<-END_PARAGRAPH
      To get the string version of an object, we simply write
      #{code '.to_s'} after it:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      var1 = 2
      var2 = '5'
      
      puts var1.to_s + var2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Similarly, #{code 'to_i'} gives the integer version of an object,
      and #{code 'to_f'} gives the float version.  Let's look at what
      these three methods do (and <em>don't</em> do) a little more closely:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      var1 = 2
      var2 = '5'
      
      puts var1.to_s + var2
      puts var1 + var2.to_i
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Notice that, even after we got the string version of
      #{code 'var1'} by calling #{code 'to_s'}, #{code 'var1'} was always pointing
      at #{code '2'}, and never at #{code "'2'"}.  Unless we explicitly reassign
      #{code 'var1'} (which requires an #{code '='} sign), it will point
      at #{code '2'} for the life of the program.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Now let's try some more interesting (and a few just weird) conversions:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts '15'.to_f
      puts '99.999'.to_f
      puts '99.999'.to_i
      puts ''
      puts '5 is my favorite number!'.to_i
      puts 'Who asked you about 5 or whatever?'.to_i
      puts 'Your momma did.'.to_f
      puts ''
      puts 'stringy'.to_s
      puts 3.to_i
      END_CODE
    end
    para do <<-END_PARAGRAPH
      So, this probably gave some surprises.  The first one is pretty
      standard, giving #{output '15.0'}.
      After that, we converted the string #{code "'99.999'"} to a float and
      to an integer.  The float did what we expected; the integer was, as always, rounded down.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Next, we had some examples of some... <em>unusual</em> strings being converted
      into numbers.  #{code 'to_i'} ignores the first thing it doesn't understand,
      and the rest of the string from that point on.  So the first one
      was converted to #{code '5'}, but the others, since they started with
      letters, were ignored completely... so the computer just picks zero.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Finally, we saw that our last two conversions did nothing at all,
      just as we would expect.
      END_PARAGRAPH
    end
    h2 {'Another Look at '+(code 'puts')}
    para do <<-END_PARAGRAPH
      There's something strange about our favorite method...  Take a look at this:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 20
      puts 20.to_s
      puts '20'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Why do these three all print the same thing?  Well, the last two
      should, since #{code '20.to_s'} <em>is</em> #{code "'20'"}.  But what
      about the first one, the integer #{code '20'}?  For that matter, what
      does it even mean to write out <em>the integer</em> 20?  When
      you write a <em>2</em> and then a <em>0</em> on a piece of paper, you
      are writing down a string, not an integer.  <em>The integer</em> 20 is the number of
      fingers and toes I have; it isn't a <em>2</em> followed by a <em>0</em>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Well, here's the big secret behind our friend, #{code 'puts'}:  Before
      #{code 'puts'} tries to write out an object, it uses #{code 'to_s'} to
      get the string version of that object.  In fact, the <em>s</em> in
      #{code 'puts'} stands for <em>string</em>; #{code 'puts'} really means
      <dfn>put string</dfn>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      This may not seem too exciting now, but there are many,
      <em>many</em> kinds of objects in Ruby (you'll even learn how
      to make your own!), and it's nice to know what will happen if
      you try to #{code 'puts'} a really weird object,
      like a picture of your grandmother, or a music file or something.
      But that will come later...
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      In the meantime, we have a few more methods for you, and they
      allow us to write all sorts of fun programs...
      END_PARAGRAPH
    end
    h2 {'The Methods '+(code 'gets')+' and '+(code 'chomp')}
    para do <<-END_PARAGRAPH
      If #{code 'puts'} means <dfn>put string</dfn>, I'm sure you can guess
      what #{code 'gets'} stands for.  And just as #{code 'puts'} always
      spits out strings, #{code 'gets'} will only retrieve strings.  And
      whence does it get them?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      From you!  Well, from your keyboard, anyway.  Since your keyboard only
      makes strings, that works out beautifully.  What actually happens
      is that #{code 'gets'} just sits there, reading what you type until
      you press <kbd>Enter</kbd>.  Let's try it out:
      END_PARAGRAPH
    end
    prog ['Is there an echo in here?'] do <<-END_CODE
      puts gets
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Of course, whatever you type in will just get repeated back
      to you.  Run it a few times and try typing in different things.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Now we can make interactive programs!  In this one, type in
      your name and it will greet you:
      END_PARAGRAPH
    end
    prog ['Chris'], '<em>Eek!</em>  I just ran it&mdash;I typed in my name, and this is what happened:' do <<-END_CODE
      puts 'Hello there, and what\\'s your name?'
      name = gets
      puts 'Your name is ' + name + '?  What a lovely name!'
      puts 'Pleased to meet you, ' + name + '.  :)'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Hmmm... it looks like when I typed in the letters <kbd>C</kbd>,
      <kbd>h</kbd>, <kbd>r</kbd>, <kbd>i</kbd>,
      <kbd>s</kbd>, and then pressed <kbd>Enter</kbd>, #{code 'gets'}
      got all of the letters in my name <em>and</em> the
      <kbd>Enter</kbd>!  Fortunately, there's a method just for
      this sort of thing:  #{code 'chomp'}.  It takes off any <kbd>Enter</kbd>s
      hanging out at the end of your string.  Let's try that program again,
      but with #{code 'chomp'} to help us this time:
      END_PARAGRAPH
    end
    prog ['Chris'] do <<-END_CODE
      puts 'Hello there, and what\\'s your name?'
      name = gets.chomp
      puts 'Your name is ' + name + '?  What a lovely name!'
      puts 'Pleased to meet you, ' + name + '.  :)'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Much better!  Notice that since #{code 'name'} is pointing to
      #{code 'gets.chomp'}, we don't ever have to say
      #{code 'name.chomp'};  #{code 'name'} was already
      #{code 'chomp'}ed.
      END_PARAGRAPH
    end
    h2 {'A Few Things to Try'}
    para do <<-END_PARAGRAPH
      &bull; Write a program which asks for a person's first name, then middle,
      then last.  Finally, it should greet the person using their full name.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Write a program which asks for a person's favorite number.
      Have your program add one to the number, then suggest the result
      as a <em>bigger and better</em> favorite number.
      (Do be tactful about it, though.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Once you have finished those two programs (and any others you would like to try),
      let's learn some more (and some more about) #{makeLink('methods', :generateMethods)}.
      END_PARAGRAPH
    end
  end
  
  #
  #  METHODS
  #
  
  def generateMethods
    para do <<-END_PARAGRAPH
      Hemos visto un número de diferentes metodos, #{code 'puts'} y  #{code 'gets'}
      , etcétera (<em><strong>Pop Quiz:</strong> Listar todos los metodos que hemos 
      visto hasta ahora! Hay diéz de ellos, la respuesta esta abajo.</em>), pero no hemos
      realmente hablado sobre que hacen los metodos.
      Sabemos que hacen, pero no lo que son.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Pero realmente, esto <em>es</em> lo que son: cosas que generan otras. 
      Si objetos(como strings, enteros, y punto flotantes) sos los sujetos en 
      el lenguaje Ruby, entonces los metodos son como verbos. Y, justo como en
      Ingles, tu no puedes tener un verbo sin un sustantivo para <em>hacer</em> el verbo.
      Por ejemplo, tic-tac no es algo que solo ocurre; un reloj(o algo) tiene que hacer
      esto. En Ingles podemos decir, "El reloj hace tic-tac". En Ruby podemos decir 
      #{code 'clock.tick'} (asumiendo que #{code 'clock'} es un objeto Ruby, por supuesto.
      Programadores pueden decir que estamos "llamando el metodo #{code 'tick'} de 
      #{code 'clock'}."
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces, has hecho la prueba? Bien. Biemo, estoy seguro 
      recordaras los metodos #{code 'puts'}, #{code 'gets'}, y
      #{code 'chomp'}, dado que ya hablamos sobre ellos. 
      Probablemente tambien recuerdas los metodos de conversión
      #{code 'to_i'}, #{code 'to_f'}, y #{code 'to_s'}. Sin embargo, 
      has visto los otros cuatro? Porque, estos no son otros que
      nuestros viejos amigos para la aritmentica #{code '+'},
      #{code '-'}, #{code '*'}, y #{code '/'}!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces como estaba diciendo, como cada verbo necesita un sustantivo,
      entonces cada metodo necesita un objeto. Esto es generalmente fácil de 
      indicar: es el que viene justo antes de un punto, como nuestro 
      ejemplo #{code 'clock.tick'}, o en #{code '101.to_s'}.
      Algunas veces, sin embargo, esto no es tan obvio; como con los metodos 
      aritmeticos. Como resulta, #{code '5 + 5'}  es solo otra forma facil de 
      escribir #{code '5.+ 5'}.
      Por ejemplo:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'hola '.+ 'mundo'
      puts (10.* 9).+ 9
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Esto no es muy lindo, por lo que no vamos a escribir siempre como ahora.
      ; sin embargo, es importante para entender que sucede <em>realmente</em>.
      (En mi pc, que también me da un <dfn>warning</dfn>:#{output 'warning: 
      parenthesize argument(s) for future version'}. Esto continua corriendo
      bien el código. pero esta diciendome que esta teniendo un problema para
      entender que estoy intentando hacer, y para usar mas parentesis en el 
      futuro.)
      Esto también nos da un profundo entendimiento de porque podemos hacer
      #{code "'pig'*5"} pero no podemos hacer #{code "5*'pig'"}: #{code "'pig'*5"}
      esta diciendo a #{code "'pig'"} de hacer la multiplicación, pero #{code "5*'pig'"} 
      esta diciendo  #{code '5'} de hacer la multiplicación. #{code "'pig'"} sabe como 
      hacer  #{code '5'} copias de si mismo y agregar todos ellos juntos; sin embargo,
      #{code '5'} tendra mucha mas dificultad en tiempo de hacer #{code "'pig'"} copias
      de si <em>mismo</em> y sumarlos a todos juntos.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Y, por supuesto, continuaremos teniendo #{code 'puts'} y #{code 'gets'} para explicar.
      Donde estan sus objetos? En Ingles, puedes algunas veces dejar fuera el sustantivo;
      por ejemplo, si un villano grita "Muere!", el sustantivo implicito es a quien el esta
      gritando. En Ruby, if digo #{code "puts 'ser o no ser'"}, lo que realmente estoy 
      diciendo es #{code "self.puts 'to be or not to be'"}.
      Entonces que es #{code 'self'}? Esta es una variable especial que apunta a cualquier 
      en el que estes. No siempre sabemos como estar <em>en</em> un objeto,pera hasta que nos
      demos cuenta, siempre iremos a estar en un gran objeto que es... el programa entero! Y 
      para nuestra suerte, el programa tendra unos pocos metodos en si mismo, como #{code 'puts'} 
      y #{code 'gets'}.
      Observa lo siguiente:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      iCantBelieveIMadeAVariableNameThisLongJustToPointToA3 = 3
      puts iCantBelieveIMadeAVariableNameThisLongJustToPointToA3
      self.puts iCantBelieveIMadeAVariableNameThisLongJustToPointToA3
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Si no alcansaste a comprender todo, esta bien. Lo importante es 
      todo metodo esta siendo propiedad de un objeto, incluso si no tiene
      un punto enfrente de este. Si entiendes esto, estas preparado.
      END_PARAGRAPH
    end
    h2 {'Fancy String Methods'}
    para do <<-END_PARAGRAPH
      Vamos a aprender unos pocos pero interesantes metodos. No tienes
      porque memorizar todos; puedes mirar esta pagina de nuevo si te
      olvidas de alguno. Yo solo quiero mostrarte una <em>pequeña</em>
      parte de lo que puede hacer un string. De hecho, no recuerdo ni
      siquiera la mitad de los metodos para strings; pero esta bien, porque
      hay buenas referencias en internet con todo acerca de los de string
      listados y explicados. (Voy a mostrarte donde encontrar esas referencias
      al final del tutorial.)
      Realmente, tampoco <em>quiero</em> saber todo acerca de los metodos string;
      sino sería como tratar de conocer cada palabra en el diccionario. Pued hablar
      Ingles bien sin conocer cada una de las palabras del diccionario... y es
      este realmente todo el objetivo del diccionario? Entonces no <em>tienes</em> 
      que saber que hay en este?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces, nuestro primer metodo string es #{code 'reverse'},
      el cual nos una version invertida de un string:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      var1 = 'parar'
      var2 = 'subrayado'
      var3 = 'Puedes pronunciar esta oración al reves?'
      
      puts var1.reverse
      puts var2.reverse
      puts var3.reverse
      puts var1
      puts var2
      puts var3
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Como puedes ver, #{code 'reverse'} no revierte el orden en el string original; este
      solo hace una nueva version de este en reversa. Esto es porque #{code 'var1'} continua
      #{code "'stop'"} aun después de que llamamos  #{code 'reverse'} sobre  #{code 'var1'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Otro metodo para strings es #{code 'length'}, el cual nos dice el numero de caracteres
      (incluyendo caracteres) en el string:
      END_PARAGRAPH
    end
    prog ['Christopher David Pine'] do <<-END_CODE
      puts 'Cuál es tu nombre completo?'
      name = gets.chomp
      puts 'Sabes que hay ' + name.length + ' caracteres en tu nombre, ' + name + '?'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Uhh!! Algo salió mal, y esto parece que ocurrio despues la linea 
      #{code 'name = gets.chomp'}... Puedes ver el problema? Fijate si puedes darte cuenta.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      El problema es con #{code 'length'}: esto te devuelve un número, pero nosotros queremos
      un string. Esto es fácil, necesitamos solo agregar #{code 'to_s'} (y cruzar nuestros dedos):
      END_PARAGRAPH
    end
    prog ['Christopher David Pine'] do <<-END_CODE
      puts 'Cuál es tu nombre completo?'
      name = gets.chomp
      puts 'Sabías que hay ' + name.length.to_s + ' caracteres en tu nombre, ' + name + '?'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      No, no conocía esto.  <strong>Nota:</strong> esto es el número de
      <em>caracteres</em> en mi nombre, no el número de <em>letras</em>. Supongo
      que podríamos escribir un programa el cual nos pregunte por nuestro primer
      nombre, medio, y apellido individualmente, y entonces sumar estos tamaños
      todos juntos... ey, porque no haces esto! Comienza, esperare.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Lo hiciste? Bien! Es un lindo programa, no? Después de unos pocos capítulos más, 
      pienso, estaras sorprendido de lo que podras hacer. 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces, hay también un número de metodos string los cuales cambian
      el contenido(mayúsculas y minúsculas) de tu string. #{code 'upcase'} 
      cambian cada minúscula por mayúscula. #{code 'swapcase'} cambia en cada
      letra en el string("Hola".swapcase  #=> "hOLA"), y finalmente, #{code 'capitalize'}
      es como #{code 'downcase'}, excepto que esto cambia solo el primer caracter a
      mayúsculas(si es una letra).
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      letters = 'aAbBcCdDeE'
      puts letters.upcase
      puts letters.downcase
      puts letters.swapcase
      puts letters.capitalize
      puts ' a'.capitalize
      puts letters
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Esto es bastante standar. Como puedes ver desde la linea #{code "puts ' a'.capitalize"},
      el método #{code 'capitalize'} solo deja en mayúsculas el primer <em>caracter</em>, no 
      la primer <em>letra</em>. También, como hemos visto antes, en todas estas llamadas a 
      metodos, , #{code 'letters'} permanece igual. No quiero decir que se dedica solo a esto,
      pero es importante entenderlo. Hay algunos metodos los cuales <em>hacen</em> cambios a los
      objetos asociados, pero no los hemos visto aún, y no lo haremos por algún tiempo. 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Lo ultimo de los metodos que veremos son los de formato visual. El primero es, #{code 'center'},
      suma espacios al comienzo y final para hacer que este centrado. Sin embargo, solo tienes
      que decir #{code 'puts'} a lo que quieres imprimir, y #{code '+'} a lo que quieres sumar, pero
      tienes que decir a #{code 'center'} cuan ancho tiene que ser el string centrado. Entonces si quiero
      centrar las lineas de un poema, debería hacer algo como esto:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      lineWidth = 50
      puts(                'Old Mother Hubbard'.center(lineWidth))
      puts(               'Sat in her cupboard'.center(lineWidth))
      puts(         'Eating her curds an whey,'.center(lineWidth))
      puts(          'When along came a spider'.center(lineWidth))
      puts(         'Which sat down beside her'.center(lineWidth))
      puts('And scared her poor shoe dog away.'.center(lineWidth))
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Mmmm.. no pienso que esto es un campamento de verano, pero estoy muy 
      cansado para buscar esto. (Entonces, quise alinear la parte 
      #{code '.center lineWidth'} , entonces puse esos espacios extras antes
      de los strings. Esto es así solo porque pienso que es mas lindo de
      esta forma. Programadores generalmente tienen duros conceptos acerca
      de que es lindo en un programa, y a menudo confrontan acerca de esto. 
      Cuanto mas programes, mas lograras tu propio estilo.)  Hablando de ser
      perezoso a la hora de programar, esto no es siempre algo malo en 
      programación. Por ejemplo, fijate como salve el ancho del poema en la
      variable  #{code 'lineWidth'}? Esto es que si entonces quiero regresar
      mas tarde y hacer el poema mas ancho, solo tengo que cambiar la variable
      al comienzo del programa, antes que en cada linea. Con un poema muy largo,
      esto podría ahorrarme un montón de tiempo. Este tipo de pereza es realmente
      una virtud en programación.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces, acerca del centrado... tu te daras cuenta que esto no es muy
      lindo como podría serlo un procesador de texto. Si realmente quieres un 
      perfecto centrado (y quizás una fuente mas linda), entonces deberías
      solo usar un procesador de textos!. Ruby es una herramienta maravillosa,
      pero no la herramienta correcta para <em>cualquier</em> trabalo.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Los otros dos metodos de formateo de strings son #{code 'ljust'} y 
      #{code 'rjust'}, lo cual significan <dfn>justificado izquierdo</dfn> y
      <dfn>justificado derecho</dfn>. Estos son similares a #{code 'center'},
      excepto que ellos rellenan los lados derecho e izquierdo respectivamente.
      Vamos a verlos en acción:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      lineWidth = 40
      str = '--> text <--'
      puts str.ljust  lineWidth
      puts str.center lineWidth
      puts str.rjust  lineWidth
      puts str.ljust (lineWidth/2) + str.rjust (lineWidth/2)
      END_CODE
    end
    h2 {'Algunas cosas mas para probar'}
    para do <<-END_PARAGRAPH
      &bull; Escribe un programa Jefe Enojado. Esto debe preguntar de mala 
      manera que quieres. Cualquier cosa que consultes, el Jefe Enojado debera
      devolverte la consulta de mala forma, y luego despedirte. Por ejemplo,
      si tu escribes #{input 'Quiero un aumento.'}, esto debera contestarte
     #{output 'PERO QUE DICES HOMBRE "QUIERO UN AUMENTO."?!?  ESTAS DESPEDIDO!!'}
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Entonces aquí hay algo para que hagas en orden de jugar un poco mas con
      #{code 'center'}, #{code 'ljust'}, y #{code 'rjust'}: Escribe un programa el 
      cual muestre una Tabla de Contenidos que se parezca a lo siguiente:
      END_PARAGRAPH
    end
    puts '<pre class="L2PoutputBlock">' +
          '                Tabla de Contenidos                 ' + $/ +
          '                                                    ' + $/ +
          'Capítulo 1:  Números                        página 1' + $/ +
          'Capítulo 2:  Lettras                       página 72' + $/ +
          'Capítulo 3:  Variables                    página 118' + $/ +
          '</pre>'
    h2 {'Matemáticas Avanzadas'}
    para do <<-END_PARAGRAPH
      <em>(Esta sección es totalmente opcional. Este asume un conocimiento
      previo de matemáticas. Si no estas interesado, puedes ir directamente
      al siguiente capitulo #{makeLink 'Flow Control', :generateFlowControl}
      sin problemas. Aunque, una rápida vista de esta sección sobre
      <strong>Random de Números</strong> debería venir bien.)</em>
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      No hay ni cerca tantos metodos numericos como los hay para strings(pienso
      que aun no los conozco a todos sin recurrir a la ayuda de documentación).
      Aquí, vamos a mirar el resto de los métodos de aritmetica, un generador
      numerico random, y el objeto #{code 'Math'} , con sus metodos trigonometricos
      y transcendental.
      END_PARAGRAPH
    end
    h2 {'Mas de aritmetica'}
    para do <<-END_PARAGRAPH
      Los otros dos metodos aritmeticos son #{code '**'} (exponencia) y #{code '%'} 
      (modulo). Entonces si quieres decir "cinco al cuadrado" en Ruby, deberías 
      escribir algo asi #{code '5**2'}. Tambien puedes usar flotantes para tus 
      exponentes, entonces si queires una raiz cuadrada de 5, deberías escribir 
      #{code '5**0.5'}. Los metodos modulo te dan el sobrante después de una división
      por un número. Entonces, por ejemlo, si divido 7 por 3, obtengo 2 con un remanente
      de 1. Vamos a ver como es que trabaja en un programa:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 5**2
      puts 5**0.5
      puts 7/3
      puts 7%3
      puts 365%7
      END_CODE
    end
    para do <<-END_PARAGRAPH
      De la ultima linea, aprendimos que un año (no bisiestos) tienen algún 
      número de semanas, más un día. Entonces si tu cumpleaños fue un Martes 
      este año, el próximo año sera un Miércoles. Tu también puedes usar 
      flotantes con los metodos modulo. Basicamente, funciona de una manera
      lógica... pero voy a mostrar un poco mas como trabajar con esto.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Hay un último método para mencionar antes de chequear el método random: 
       #{code 'abs'}. Este solo toma el valor absoluto de un número:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts((5-2).abs)
      puts((2-5).abs)
      END_CODE
    end
    h2 {'Random Numerico'}
    para do <<-END_PARAGRAPH
      Ruby viene con un lindo generador de números random. El método para obtener
      un número random es #{code 'rand'}. Si llamas #{code 'rand'} , obtendras un
      número flotante mayor o igual a #{code '0.0'} y menor a #{code '1.0'}. Si
      le proporcionas a #{code 'rand'} un número entero (#{code '5'} for example),
      esto te devolvera un entero mayor o igual a #{code '0'} y menor a #{code '5'} 
      (entonces son cinco números posibles, de #{code '0'} a #{code '4'}).
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Vamos a ver #{code 'rand'}  en accion. (Si recargas esta página, veras que
      el número cambiara cada vez. Tu sabías que estoy corriendo estos programas, 
      lo sabías?!?!
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts rand
      puts rand
      puts rand
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      puts(rand(1))
      puts(rand(1))
      puts(rand(1))
      puts(rand(99999999999999999999999999999999999999999999999999999999999))
      puts('El pronosticador del tiempo dijo que hay '+rand(101).to_s+'% chances de que llueva,')
      puts('pero nunca debes confiar en el.')
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Fijate que utilice #{code 'rand(101)'} para obtener números entre #{code '0'}
      y #{code '100'}, y que el #{code 'rand(1)'} siempre devuelve #{code '0'}. No
      entender el rango posible de retorno de valores es el error mas grande que veo
      en gente que hace #{code 'rand'}; aún programadores profesionales, mas aun en 
      productos finalizados que puedes comprar. Incluso tenía un reproductor de CD, 
      una vez que, si se configuraba en "Reproducción aleatoria," reproduciría jugaría 
      cada canción, pero no la última ... (Me pregunto qué hubiera pasado si hubiera 
      puesto en un CD con sólo una canción sobre ella?)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Algunas veces querras que #{code 'rand'} retorne el <em>mismo</em>
      random de números incluso en la misma secuencia en dos diferentes ejecuciones
      de tu programa. (Por ejemplo, una vez estaba utilizando numeros generados 
      aleatoriamente para crear un mundo al azar por un juego de computadoras.
      Encontre un mundo que realmente me gusto, quizas me hubiera gustado jugar de nuevo
      con este o enviarlo a un amigo.) Con el fin de hacer esto, tu necesitas configurar 
      la <em>"generacion de este"</em>, lo que se puede hacer con #{code 'srand'}. Como 
      lo siguiente:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      srand 1776
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      puts ''
      srand 1776
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      puts(rand(100))
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Esto hara la misma cosa cada vez que inicies con el mismo número. Si quieres
      obtener diferentes números(como pasaría si nunca utilizaras #{code 'srand'}), 
      entonces solo llamas a #{code 'srand 0'}. Esto inicializa con un número 
      realmente raro, utilizando (ademas de otras cosas) la hora actual de tu 
      computadora, hasta los milisegundos.
      END_PARAGRAPH
    end
    h2 {"El Objeto #{code 'Math'}"}
    para do <<-END_PARAGRAPH
      Finalmente, vamos a echar un vistazo al objeto #{code 'Math'}. Deveríamos
      ir directamene a este:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts(Math::PI)
      puts(Math::E)
      puts(Math.cos(Math::PI/3))
      puts(Math.tan(Math::PI/4))
      puts(Math.log(Math::E**2))
      puts((1 + Math.sqrt(5))/2)
      END_CODE
    end
    para do <<-END_PARAGRAPH
      La primera cosa de la que te habras dado cuenta es probablemente de
      la notación #{code '::'}. Explicando el <dfn>alcance del operador</dfn>
      (que es esto) esta realmente , fuera del objetivo de este tutorial.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Como puedes ver, #{code 'Math'} tiene todas las cosas que podrias 
      esperar de una calculadora científica decente. Y como siempre, los
      punto flotante estan <em>realmente cerca</em> de ser la respuesta
      correcta.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces ahora vamos a  #{makeLink 'flow', :generateFlowControl}!
      END_PARAGRAPH
    end
  end
  
  #
  #  FLOW CONTROL
  #
  
  def generateFlowControl
    para do <<-END_PARAGRAPH
      Ahhhh, flow control.  This is where it all comes together.  Even though
      this chapter is shorter and easier than the #{makeLink 'methods', :generateMethods}
      chapter, it will open up a whole world of programming possibilities.
      After this chapter, we'll be able to write truly interactive
      programs; in the past we have made programs which <em>say</em> different
      things depending on your keyboard input, but after this chapter
      they will actually <em>do</em> different things, too.  But
      before we can do that, we need to be
      able to compare the objects in our programs.  We need...
      END_PARAGRAPH
    end
    h2 {'Comparison Methods'}
    para do <<-END_PARAGRAPH
      Let's rush through this part so we can get to the next
      section, <strong>Branching</strong>, where all the cool
      stuff happens.  So, to see if one object is greater than
      or less than another, we use the methods #{code '>'}
      and #{code '<'}, like this:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 1 > 2
      puts 1 < 2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      No problem.  Likewise, we can find out if an object is
      greater-than-or-equal-to another (or less-than-or-equal-to)
      with the methods #{code '>='} and #{code '<='}
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 5 >= 5
      puts 5 <= 4
      END_CODE
    end
    para do <<-END_PARAGRAPH
      And finally, we can see if two objects are equal or not
      using #{code '=='} (which means "are these equal?")
      and #{code '!='} (which means "are these different?").
      It's important not to confuse #{code '='} with #{code '=='}.
      #{code '='} is for telling a variable to point at an object
      (assignment), and #{code '=='} is for asking the question:  "Are
      these two objects equal?"
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 1 == 1
      puts 2 != 1
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Of course, we can compare strings, too.  When strings
      get compared, they compare their <dfn>lexicographical ordering</dfn>,
      which basically means their dictionary ordering.  #{code 'cat'}
      comes before #{code 'dog'} in the dictionary, so:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts 'cat' < 'dog'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      There's a catch, though:  the way computers usually do things,
      they order capital letters as coming before lowercase letters.
      (That's how they store the letters in fonts, for example:
      all the capital letters first, then the lowercase ones.)
      This means that it will think #{code "'Zoo'"} comes before #{code "'ant'"}, so if you
      want to figure out which word would come first in a real dictionary,
      make sure to use #{code 'downcase'} (or #{code 'upcase'} or
      #{code 'capitalize'}) on both words before you try to compare them.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      One last note before <strong>Branching</strong>:  The comparison
      methods aren't giving us the strings #{code "'true'"} and
      #{code "'false'"}; they are giving us the special objects #{code 'true'} and
      #{code 'false'}.  (Of course, #{code 'true.to_s'} gives us
      #{code "'true'"}, which is why #{code 'puts'} printed #{code "'true'"}.)
      #{code 'true'} and #{code 'false'} are used all the time in...
      END_PARAGRAPH
    end
    h2 {'Branching'}
    para do <<-END_PARAGRAPH
      Branching is a simple concept, but powerful.  In fact, it's so simple
      that I bet I don't even have to explain it at all; I'll just show you:
      END_PARAGRAPH
    end
    run1 = {:input => ['Chris']}
    run2 = {:input => ['Chewbacca'], :remark => 'But if we put in a different name...'}
    progN run1, run2 do <<-END_CODE
      puts 'Hello, what\\'s your name?'
      name = gets.chomp
      puts 'Hello, ' + name + '.'
      if name == 'Chris'
        puts 'What a lovely name!'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      And that is branching.  If what comes after the #{code 'if'} is
      #{code 'true'}, we run the code between the
      #{code 'if'} and the #{code 'end'}.  If what comes after the
      #{code 'if'} is #{code 'false'}, we don't.  Plain and simple.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      I indented the code between the #{code 'if'} and the #{code 'end'}
      just because I think it's easier to keep track of the
      branching that way.  Almost all
      programmers do this, regardless of what language they are
      programming in.  It may not seem much help in this simple
      example, but when things get more complex, it makes a big
      difference.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Often, we would like a program to do one thing if an expression
      is #{code 'true'}, and another if it is #{code 'false'}.  That's
      what #{code 'else'} is for:
      END_PARAGRAPH
    end
    run1 = {:input => ['Chris']}
    run2 = {:input => ['Ringo'], :remark => 'Now let\'s try a different name...'}
    progN run1, run2 do <<-END_CODE
      puts 'I am a fortune-teller.  Tell me your name:'
      name = gets.chomp
      if name == 'Chris'
        puts 'I see great things in your future.'
      else
        puts 'Your future is... Oh my!  Look at the time!'
        puts 'I really have to go, sorry!'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Branching is kind of like coming to a fork in the code:  Do
      we take the path for people whose #{code "name == 'Chris'"},
      or #{code 'else'} do we take the other path?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      And just like the branches of a tree, you can have branches
      which themselves have branches:
      END_PARAGRAPH
    end
    run1 = {:input => ['chris', 'yes']}
    run2 = {:input => ['Chris'], :remark => 'Fine, I\'ll capitalize it...'}
    progN run1, run2 do <<-END_CODE
      puts 'Hello, and welcome to 7th grade English.'
      puts 'My name is Mrs. Gabbard.  And your name is...?'
      name = gets.chomp
      
      if name == name.capitalize
        puts 'Please take a seat, ' + name + '.'
      else
        puts name + '?  You mean ' + name.capitalize + ', right?'
        puts 'Don\\'t you even know how to spell your name??'
        reply = gets.chomp
        
        if reply.downcase == 'yes'
          puts 'Hmmph!  Well, sit down!'
        else
          puts 'GET OUT!!'
        end
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Sometimes it might get confusing trying to figure out
      where all of the #{code 'if'}s, #{code 'else'}s, and
      #{code 'end'}s go.  What I do is write the #{code 'end'}
      <em>at the same time</em> I write the #{code 'if'}.  So
      as I was writing the above program, this is how it looked
      first:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 'Hello, and welcome to 7th grade English.'
      puts 'My name is Mrs. Gabbard.  And your name is...?'
      name = gets.chomp
      
      if name == name.capitalize
      else
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Then I filled it in with <dfn>comments</dfn>, stuff
      in the code the computer will ignore:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 'Hello, and welcome to 7th grade English.'
      puts 'My name is Mrs. Gabbard.  And your name is...?'
      name = gets.chomp
      
      if name == name.capitalize
        #  She's civil.
      else
        #  She gets mad.
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Anything after a #{code '#'} is
      considered a comment (unless, of course, you
      are in a string).  After that, I replaced the comments
      with working code.  Some people like to leave the comments
      in; personally, I think well-written code usually speaks
      for itself.  I used to use more comments, but the more
      "fluent" in Ruby I become, the less I use them.  I actually
      find them distracting much of the time.  It's a personal
      choice; you'll find your own (usually evolving) style.
      So my next step looked like this:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      puts 'Hello, and welcome to 7th grade English.'
      puts 'My name is Mrs. Gabbard.  And your name is...?'
      name = gets.chomp
      
      if name == name.capitalize
        puts 'Please take a seat, ' + name + '.'
      else
        puts name + '?  You mean ' + name.capitalize + ', right?'
        puts 'Don\\'t you even know how to spell your name??'
        reply = gets.chomp
        
        if reply.downcase == 'yes'
        else
        end
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Again, I wrote down the #{code 'if'}, #{code 'else'}, and
      #{code 'end'} all at the same time.  It really helps me keep
      track of "where I am" in the code.  It also makes the job
      seem easier because I can focus on one small part, like
      filling in the code between the #{code 'if'} and the
      #{code 'else'}.  The other benefit of doing it this way
      is that the computer can understand the program at any
      stage.  Every one of the unfinished versions of the
      program I showed you would run.  They weren't finished,
      but they were working programs.  That way I could test it
      as I wrote it, which helped to see how it was coming along
      and where it still needed work.  When it passed all
      of the tests, that's how I knew I was done!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      These tips will help you write programs with branching,
      but they also help with the other main type of flow control:
      END_PARAGRAPH
    end
    h2 {'Looping'}
    para do <<-END_PARAGRAPH
      Often, you'll want your computer to do the same thing over and
      over again&mdash;after all, that's what computers are supposed to
      be so good at.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      When you tell your computer to keep repeating something,
      you also need to tell it when to stop.  Computers never get bored,
      so if you don't tell it to stop, it won't.  We make sure this
      doesn't happen by telling the computer to repeat certain parts
      of a program #{code 'while'} a certain condition is true.  This
      works very similarly to how #{code 'if'} works:
      END_PARAGRAPH
    end
    prog ['Hello?', 'Hi!', 'Very nice to meet you.', 'Oh... how sweet!', 'bye'] do <<-END_CODE
      command = ''
      
      while command != 'bye'
        puts command
        command = gets.chomp
      end
      
      puts 'Come again soon!'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      And that's a loop.  (You may have noticed the blank line at the
      beginning of the output; it's from the first #{code 'puts'}, before
      the first #{code 'gets'}.  How would you change the program to get
      rid of this first line.  Test it!  Did it work <em>exactly</em>
      like the program above, other than that first blank line?)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Loops allow you to do all kinds of interesting things, as I'm sure
      you can imagine.  However, they can also cause problems if you
      make a mistake.  What if your computer gets trapped in an infinite
      loop?  If you think this may have happened, just hold down the
      <kbd>Ctrl</kbd> key and press <kbd>C</kbd>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Before we start playing around with loops, though,
      let's learn a few things to make our job easier.
      END_PARAGRAPH
    end
    h2 {'A Little Bit of Logic'}
    para do <<-END_PARAGRAPH
      Let's take a look at our first branching program again.  What if
      my wife came home, saw the program, tried it out, and it didn't
      tell her what a lovely name <em>she</em> had?  I wouldn't want to
      hurt her feelings (or sleep on the couch), so let's rewrite it:
      END_PARAGRAPH
    end
    prog ['Katy'] do <<-END_CODE
      puts 'Hello, what\\'s your name?'
      name = gets.chomp
      puts 'Hello, ' + name + '.'
      if name == 'Chris'
        puts 'What a lovely name!'
      else
        if name == 'Katy'
          puts 'What a lovely name!'
        end
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Well, it works... but it isn't a very pretty program.  Why not?
      Well, the best
      rule I ever learned in programming was the <dfn>DRY</dfn> rule:
      <dfn>Don't Repeat Yourself</dfn>.  I could probably write a small
      book just on why that is such a good rule.  In our case, we
      repeated the line #{code "puts 'What a lovely name!'"}.  Why is
      this such a big deal?  Well, what if I made a spelling mistake
      when I rewrote it?  What if I wanted to change it from
      #{code "'lovely'"} to #{code "'beautiful'"} on both lines?
      I'm lazy, remember?  Basically, if
      I want the program to do the same thing when it gets
      #{code "'Chris'"} or #{code "'Katy'"}, then it should really
      <em>do the same thing</em>:
      END_PARAGRAPH
    end
    prog ['Katy'] do <<-END_CODE
      puts 'Hello, what\\'s your name?'
      name = gets.chomp
      puts 'Hello, ' + name + '.'
      if (name == 'Chris' or name == 'Katy')
        puts 'What a lovely name!'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Much better.  In order to make it work, I used #{code 'or'}.
      The other <em>logical operators</em> are #{code 'and'} and 
      #{code 'not'}.  It is always a good idea to use parentheses
      when working with these.  Let's see how they work:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      iAmChris  = true
      iAmPurple = false
      iLikeFood = true
      iEatRocks = false
      
      puts (iAmChris  and iLikeFood)
      puts (iLikeFood and iEatRocks)
      puts (iAmPurple and iLikeFood)
      puts (iAmPurple and iEatRocks)
      puts
      puts (iAmChris  or iLikeFood)
      puts (iLikeFood or iEatRocks)
      puts (iAmPurple or iLikeFood)
      puts (iAmPurple or iEatRocks)
      puts
      puts (not iAmPurple)
      puts (not iAmChris )
      END_CODE
    end
    para do <<-END_PARAGRAPH
      The only one of these which might trick you is
      #{code 'or'}.  In English, we often use "or" to mean
      "one or the other, but not both."  For example, your
      mom might say, "For dessert, you can have pie or cake."
      She did <em>not</em> mean you could have them both!
      A computer, on the other hand, uses #{code 'or'} to mean "one or the other,
      or both."  (Another way of saying it is, "at least one of
      these is true.")  This is why computers are more fun than
      moms.
      END_PARAGRAPH
    end
    h2 {'A Few Things to Try'}
    para do <<-END_PARAGRAPH
      &bull; <em>"99 bottles of beer on the wall..."</em>  Write a program
      which prints out the lyrics to that beloved classic, that
      field-trip favorite: "99 Bottles of Beer on the Wall."
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Write a Deaf Grandma program.  Whatever you say
      to grandma (whatever you type in), she should respond with
      #{output 'HUH?!  SPEAK UP, SONNY!'}, unless you shout it (type in
      all capitals).  If you shout, she can hear you (or at least
      she thinks so) and yells back, #{output 'NO, NOT SINCE 1938!'}  To
      make your program <em>really</em> believable, have grandma
      shout a different year each time; maybe any year at random
      between 1930 and 1950.  (This part is optional, and would be
      much easier if you read the section on Ruby's random number
      generator at the end of the #{makeLink 'methods', :generateMethods}
      chapter.)  You can't stop talking to grandma
      until you shout #{input 'BYE'}.<br />
      <em><strong>Hint:</strong>  Don't forget about
      </em>#{code 'chomp'}<em>!  </em>#{code "'BYE'"}<em>with an
      Enter is not the same as </em>#{code "'BYE'"}<em> without
      one!</em><br />
      <em><strong>Hint 2:</strong>  Try to think about what parts
      of your program should happen over and over again.  All
      of those should be in your </em>#{code 'while'}<em> loop.</em>
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Extend your Deaf Grandma program:  What if grandma
      doesn't want you to leave?  When you shout #{input 'BYE'}, she
      could pretend not to hear you.  Change your previous
      program so that you have to shout #{input 'BYE'} three times
      <em>in a row</em>.  Make sure to test your program:
      if you shout #{input 'BYE'} three times, but not in a row, you
      should still be talking to grandma.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Leap Years.  Write a program which will ask for
      a starting year and an ending year, and then #{code 'puts'}
      all of the leap years between them (and including them,
      if they are also leap years).  Leap years are years divisible
      by four (like 1984 and 2004).  However, years divisible
      by 100 are <em>not</em> leap years (such as 1800 and
      1900) <strong><em>unless</em></strong> they are divisible
      by 400 (like 1600 and 2000, which were in fact leap years).
      <em>(Yes, it's all pretty
      confusing, but not as confusing has having July in the
      middle of the winter, which is what would eventually
      happen.)</em>
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      When you finish those, take a break!  You've learned a lot
      already.  Congratulations!  Are you surprised at the number
      of things you can tell a computer to do?  A few more chapters
      and you'll be able to program just about anything.  Seriously!
      Just look at all the things you can do now that you couldn't
      do without looping and branching.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Now let's learn about a new kind of
      object, one which keeps track of lists of other objects:
      #{makeLink 'arrays', :generateArrays}.
      END_PARAGRAPH
    end
  end
  
  #
  #  ARRAYS AND ITERATORS
  #
  
  def generateArrays
    para do <<-END_PARAGRAPH
      Vamos a escribir un programa el cual nos pida  tipear tantas
      palabras como nosotros querramos(una palabra por linea), 
      continuando hasta que oprimamos <kbd>Enter</kbd> en una linea
      vacia), el cual luego nos devolvera las palabras en orden 
      alfabetico. OK?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces... nosotros primero vamos &mdash;uh... um... hmmm...  Bueno
      , nosotros podríamos&mdash;er...
      um... 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Usted sabe, no pienso que podamos hacer esto. Necesitamos una 
      forma de almacenar una cantidad desconocida de palabras, y como
      obtener todas ellas juntas, entonces no se confundan con otras 
      variables. Necesitamos colocarlas en un tipo de lista. Lo que
      necesitamos son <dfn>arrays</dfn>. 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Un array es solo una lista en su computadora. Cada  posicion en 
      la lista actua como una variable: puedes ver que objeto en 
      particular apunta a cada posicion, y puedes hacer que este apunte
      a un objeto diferente. Vamos a echar un vistazo a algunos arrays:
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      []
      [5]
      ['Hola', 'Adios']
      
      flavor = 'vanilla'             #  Esto no es un array, porsupuesto...
      [89.9, sabor, [true, false]]  #  ...pero esto si lo es.
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Entonces primero tenemos un array vacio, luego un array
      conteniendo un simple numero, luego un array que contiene
      dos strings. Siguiendo, tenemos una simple asignacion, luego
      un array conteniendo tres objetos, de los cuales el último 
      es el array #{code '[true, false]'}. Recuerda, variables
      no son objetos, entonces nuestro ultimo array es en realidad
      un punto flotante, un <em>string</em>, y un array. Aun asi si
      nosotros hubieramos seteado #{code 'sabor'} a punto o algo mas, 
      esto no hubiera cambiado el array.

      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Para ayudarnos a encontrar un objeto particular en un array,
      para cada posicion es dado un indice numerico. Programadores
      (and, por cierto, la mayoría de los matemáticos) comienzan 
      contando desde cero, por lo que la primera posicion del array
      es cero.  Aquí es como nosotros deberíamos referenciar los 
      objetos en un array:

      END_PARAGRAPH
    end
    prog do <<-END_CODE
      names = ['Ada', 'Belle', 'Chris']
      
      puts names
      puts names[0]
      puts names[1]
      puts names[2]
      puts names[3]  #  Este esta fuera del rango.
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Entonces, nosotros vemos que #{code 'puts names'} imprime
      cada nombre en el array  #{code 'names'}. Luego usamos
      #{code 'puts names[0]'} para imprimir el "primer" nombre en 
      el array, y #{code 'puts names[1]'} para imprimir el "segundo"
      ... Estoy seguro que esto parece confuso, pero tu <em>puedes</em> 
      acostumbrarte a esto. Tienes que realmente solo comenzar <em>
      pensando</em> que el contador comienza en cero, y dejas de usar
      palabras como "primero" y "segundo"
      Si tu vas a un menu de cinco platos, no hablas acerca del "primer"
      curso, hablas acerca del curso cero(y en tu cabeza, estas pensando
      #{code 'course[0]'}). Tu tienes cinco dedos en tu mano derecha,
      y sus números son 0, 1, 2, 3 y 4. Mi espoza y yo somos malabaristas.
      Cuando hacemos malabares con seis objetos, nosotros estamos con 
      los objetos 0-5. Esperamos en los próximos meses poder manejarnos
      con el objeto 6(y por lo tanto trataremos de manejarnos con 7 objetos) 
      Tu sabras que lo has aprendido cuando comienzes a usar la palabra 
      "cero". Sí, esto es real; pregunta a cualquier programador o 
       matemático.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Finalmente, tratamos #{code 'puts names[3]'}, solo para ver 
      que podría suceder. Estabamos esperando un error? Algunas veces
      cuando preguntas algo, tu pregunta no tiene sentido(al menos para
      tu computadora); ahí es cuando obtienes un error.      
      Algunas veces, en cambio, tu puedes preguntar algo y la 
      respuesta es <em>nada</em>. Que es la posicion tres? Nada.
      Que es  #{code 'names[3]'}?  #{code 'nil'}: Es la forma Ruby
      de decir "nada". #{code 'nil'}  es un objeto especial lo cual
      significa "no hay ningún objeto".

      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Si todo este divertido numerado de posiciones esta molestandote,
      no te preocupes! También, podemos evitar esto completamente usando
      varios metodos array, como el que sigue:
      END_PARAGRAPH
    end
    h2 {"The Method #{code 'each'}"}
    para do <<-END_PARAGRAPH
      #{code 'each'} nos permite hacer algo(lo que quieramos)
      a #{code 'each'} objeto que apunte. Asi, is queremos decir algo
      bueno acercah de cada lenguaje en el array abajo, podriamos hacer
      esto:      
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      lenguajes = ['English', 'German', 'Ruby']
      
      lenguajes.each do |leng|
        puts 'Me gusta ' + leng + '!'
        puts 'A ti?'
      end
      
      puts 'Y vamos a escuchar esto para C++!'
      puts '...'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Que acaba de ocurrir? Bueno, tenemos permitido ir a travez
      de cada objeto en el array sin utilizar ningun número, así 
      esto es definitivamente mejor. Traducido al castellano 
      diriamos que: Para cada #{code 'each'} objeto en #{code 'lenguajes'}
      , apunta la variable #{code 'leng'} al objeto y entonces #{code 'do'}
      (do = hacer) todo lo que te digo, hasta que llegues al #{code 'end'}.
      (Solo para que sepas, C++ es otro lenguaje de programacion. Este es 
       mucho mas difícil de aprender que Ruby; por lo general, un programa
       hecho en C++ sera muchas veces mas extenso que un programa en Ruby
       que haga la misma funcionalidad)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Tu estaras pensando para ti mismo, "Esto es un monton de bucles 
      como los que hemos aprendido antes". Sí, esto es similar. 
      Una diferencia importante es que el método #{code 'each'} es solo eso:
      un método. #{code 'while'} y #{code 'end'} (tal como #{code 'do'}, 
      #{code 'if'}, #{code 'else'}, y todos las otras 
      <span class="L2Pcode"><span class="L2Pkeyword">#{@@KEYWORD_COLOR}</span></span>
      palabras no lo son. Ellos son una parte fundamental del lenguaje Ruby
      , tal como #{code '='} y las parentesis; tipos de puntuacion como en Ingles
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Pero no  #{code 'each'}; #{code 'each'} is solo otro metodo del array.
      Metodos como #{code 'each'} los cuales 'actuan como' bucles son a menudo
      llamados <dfn>iterators</dfn>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Algo para saber sobre iteradores es que estos son siempre seguidos por 
      #{code 'do'}...#{code 'end'}. 
      #{code 'while'} y #{code 'if'} nunca tuvieron un #{code 'do'} cerca de ellos;
      nosotros solo usamos #{code 'do'} con iteradores
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Aquí hay otro pequeño iterador, pero esto no es un metodo array... es un metodo
      integer!
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      3.times do
        puts 'Hip-Hip-Hooray!'
      end
      END_CODE
    end
    h2 {'Mas métodos Array'}
    para do <<-END_PARAGRAPH
      Entonces hemos aprendido sobre #{code 'each'}, pero hay muchos metodos
      mas... al menos muchos como metodos strings! De hecho, algunos de ellos
      (como #{code 'length'}, #{code 'reverse'}, #{code '+'}, y #{code '*'})
      trabajan igual que lo hacen para strings, excepto que ellos operan sobre
      las posiciones de un array y no sobre letras de un string. Otros, como
      #{code 'last'} y #{code 'join'}, son especificos de arrays. Aún otros, 
      como #{code 'push'} y #{code 'pop'}, en realidad cambian el array. Y
      asi como con metodos para strings, no tienen que recordar todos, puedes
      recurrir a recordar sobre ellos(justo aquí)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Primero, vamos a echar un vistazo a #{code 'to_s'} y #{code 'join'}.
      #{code 'join'} trabaja tal como #{code 'to_s'} lo hace, excepto que 
      este agrega un string entre los objetos del array.
      Vamos a mirar un poco:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      foods = ['artichoke', 'brioche', 'caramel']
      
      puts foods
      puts
      puts foods.to_s
      puts
      puts foods.join(', ')
      puts
      puts foods.join('  :)  ') + '  8)'
      
      200.times do
        puts []
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Como puedes ver, #{code 'puts'} trata el array diferente  a otros objetos: 
      este solo llama #{code 'puts'} sobre cada uno de los objetos en el array. 
      Esto es porque #{code 'puts'}ing un array vacio 200 veces no hace nada; el 
      array no apunta a nada; entonces no hay nada para #{code 'puts'}. (Hacer nada
      200 veces continua siendo hacer nada)
      Trata de usar #{code 'puts'} en un array conteniendo otros arrays; hace lo 
      que esperabas que hiciera?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      También, te habras dado cuenta que deje fuera el string vacio cuando quise 
      hacer #{code 'puts'} de una linea en blanco? Esto hace lo mismo.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Ahora vamos a echar un vistazo a #{code 'push'}, #{code 'pop'}, y  #{code 'last'}.  
      Los metodos #{code 'push'} y #{code 'pop'} son una suerte de metodos opuestos como
      lo son #{code '+'} y #{code '-'}. #{code 'push'} agrega un objeto al final del array,
      y #{code 'pop'} quita el último objeto desde el array(y te dice que objeto es). 
      #{code 'last'} es similar a #{code 'pop'} en el que este te indica que hay al final 
      del array, excepto que este deja el array. De nuevo, #{code 'push'} y #{code 'pop'} <em>
      en realidad cambian el array</em>:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      favorites = []
      favorites.push 'raindrops on roses'
      favorites.push 'whiskey on kittens'
      
      puts favorites[0]
      puts favorites.last
      puts favorites.length
      
      puts favorites.pop
      puts favorites
      puts favorites.length
      END_CODE
    end
    h2 {'Unas pocas cosas a probar'}
    para do <<-END_PARAGRAPH
      &bull; Escribe el programa del cual hablamos al principio de este capitulo.<br />
      <em><strong>Consejo:</strong>  Hay un hermoso metodo de arrays el cual te dara la 
      version ordenada de un array:  </em>#{code 'sort'}<em>.  Usalo!</em>
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Trata escribiendo el programa sugerido anteriormente <em>sin</em> usar
      el metodo #{code 'sort'} .  Una gran parte de la programacion es la solucion de
      problemas, entonces obtienes toda la practica que puedas!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Reescribe tu programa Tabla de contenidos (desde el capítulo sobre #{makeLink 'methods', :generateMethods}).
      Comienza el programa con un array conteniendo toda la informacion de tu Tabla de Contenidos(capitulo nombres, 
      capitulo numeros, etc.). Entonces imprime la información desde el array en una bien formada Tabla de Contenidos.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
	  Hemos aprendido un numero de diferentes metodos.
      Ahora es tiempo de aprender como #{makeLink 'hacerlo por nosotros mismos', :generateDefMethod}.
      END_PARAGRAPH
    end
  end
  
  #
  #  WRITING METHODS
  #
  
  def generateDefMethod
    para do <<-END_PARAGRAPH
      As we've seen, loops and iterators allow us to do the
      same thing (run the same code) over and over again.
      However, sometimes we want to do the same thing a
      number of times, but from different places in the program.
      For example, let's say we were writing a questionnaire
      program for a psychology student.  From the psychology
      students I have known and the questionnaires they have
      given me, it would probably go something like this:
      END_PARAGRAPH
    end
    prog ['yes','yes','no way!','NO','yes','yes'] do <<-END_CODE
      puts 'Hello, and thank you for taking the time to'
      puts 'help me with this experiment.  My experiment'
      puts 'has to do with the way people feel about'
      puts 'Mexican food.  Just think about Mexican food'
      puts 'and try to answer every question honestly,'
      puts 'with either a "yes" or a "no".  My experiment'
      puts 'has nothing to do with bed-wetting.'
      puts
      
      #  We ask these questions, but we ignore their answers.
      
      goodAnswer = false
      while (not goodAnswer)
        puts 'Do you like eating tacos?'
        answer = gets.chomp.downcase
        if (answer == 'yes' or answer == 'no')
          goodAnswer = true
        else
          puts 'Please answer "yes" or "no".'
        end
      end
      
      goodAnswer = false
      while (not goodAnswer)
        puts 'Do you like eating burritos?'
        answer = gets.chomp.downcase
        if (answer == 'yes' or answer == 'no')
          goodAnswer = true
        else
          puts 'Please answer "yes" or "no".'
        end
      end
      
      #  We pay attention to *this* answer, though.
      goodAnswer = false
      while (not goodAnswer)
        puts 'Do you wet the bed?'
        answer = gets.chomp.downcase
        if (answer == 'yes' or answer == 'no')
          goodAnswer = true
          if answer == 'yes'
            wetsBed = true
          else
            wetsBed = false
          end
        else
          puts 'Please answer "yes" or "no".'
        end
      end
      
      goodAnswer = false
      while (not goodAnswer)
        puts 'Do you like eating chimichangas?'
        answer = gets.chomp.downcase
        if (answer == 'yes' or answer == 'no')
          goodAnswer = true
        else
          puts 'Please answer "yes" or "no".'
        end
      end
      
      puts 'Just a few more questions...'
      
      goodAnswer = false
      while (not goodAnswer)
        puts 'Do you like eating sopapillas?'
        answer = gets.chomp.downcase
        if (answer == 'yes' or answer == 'no')
          goodAnswer = true
        else
          puts 'Please answer "yes" or "no".'
        end
      end
      
      #  Ask lots of other questions about Mexican food.
      
      puts
      puts 'DEBRIEFING:'
      puts 'Thank you for taking the time to help with'
      puts 'this experiment.  In fact, this experiment'
      puts 'has nothing to do with Mexican food.  It is'
      puts 'an experiment about bed-wetting.  The Mexican'
      puts 'food was just there to catch you off guard'
      puts 'in the hopes that you would answer more'
      puts 'honestly.  Thanks again.'
      puts
      puts wetsBed
      END_CODE
    end
    para do <<-END_PARAGRAPH
      That was a pretty long program, with lots of repetition.
      (All of the sections of code around the questions about Mexican food
      were identical, and the bed-wetting question was only
      slightly different.)
      Repetition is a bad thing.  Still, we can't make it into
      a big loop or iterator, because sometimes we have things
      we want to do between questions.  In situations like these,
      it's best to write a method.  Here's how:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def sayMoo
        puts 'mooooooo...'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Uh... our program didn't #{code 'sayMoo'}.
      Why not?  Because we didn't tell it to.
      We told it <em>how</em> to #{code 'sayMoo'},
      but we never actually said to <em>do</em> it.
      Let's give it another shot:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def sayMoo
        puts 'mooooooo...'
      end
      
      sayMoo
      sayMoo
      puts 'coin-coin'
      sayMoo
      sayMoo
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Ahhh, much better.  (Just in case you don't speak
      French, that was a French duck in the middle of the
      program.  In France, ducks say <em>"coin-coin"</em>.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So we <span class="L2Pkeyword">#{code 'def'}</span>ined
      the method #{code 'sayMoo'}.  (Method names, like
      variable names, start with a lowercase letter.
      There are a few exceptions, though, like #{code '+'}
      or #{code '=='}.)
      But don't methods always have to be associated with
      objects?  Well, yes they do, and in this case (as with
      #{code 'puts'} and #{code 'gets'}), the method is just
      associated with the object representing
      the whole program.  In the next chapter we'll see how to
      add methods to other objects.  But first...
      END_PARAGRAPH
    end
    h2 {'Method Parameters'}
    para do <<-END_PARAGRAPH
      You may have noticed that some methods (like
      #{code 'gets'}, #{code 'to_s'}, #{code 'reverse'}...)
      you can just call on an object.  However, other methods
      (like #{code '+'}, #{code '-'}, #{code 'puts'}...)
      take <dfn>parameters</dfn> to tell the object how to
      do the method.  For example, you wouldn't just say
      #{code '5+'}, right?  You're telling #{code '5'} to
      add, but you aren't telling it <em>what</em>
      to add.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      To add a parameter to #{code 'sayMoo'} (let's say, the
      number of moos), we would do this:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def sayMoo numberOfMoos
        puts 'mooooooo...'*numberOfMoos
      end
      
      sayMoo 3
      puts 'oink-oink'
      sayMoo  #  This should give an error because the parameter is missing.
      END_CODE
    end
    para do <<-END_PARAGRAPH
      #{code 'numberOfMoos'} is a variable which points to
      the parameter passed in.  I'll say that again, but it's
      a little confusing:  #{code 'numberOfMoos'} is a variable
      which points to the parameter passed in.  So if I type in
      #{code 'sayMoo 3'}, then the parameter is #{code '3'},
      and the variable #{code 'numberOfMoos'} points to #{code '3'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      As you can see, the parameter is now <em>required</em>.
      After all, what is #{code 'sayMoo'} supposed to multiply
      #{code "'mooooooo...'"} by if you don't give it a
      parameter?  Your poor computer has no idea.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      If objects in Ruby are like nouns in English, and methods
      are like verbs, then you can think of parameters as
      adverbs (like with #{code 'sayMoo'}, where the parameter
      told us <em>how</em> to #{code 'sayMoo'}) or sometimes as
      direct objects (like with #{code 'puts'}, where the
      parameter is <em>what</em> gets #{code 'puts'}ed).
      END_PARAGRAPH
    end
    h2 {'Local Variables'}
    para do <<-END_PARAGRAPH
      In the following program, there are two variables:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def doubleThis num
        numTimes2 = num*2
        puts num.to_s+' doubled is '+numTimes2.to_s
      end
      
      doubleThis 44
      END_CODE
    end
    para do <<-END_PARAGRAPH
      The variables are #{code 'num'} and #{code 'numTimes2'}.
      They both sit inside the method #{code 'doubleThis'}.
      These (and all of the variables you have seen
      so far) are <dfn>local variables</dfn>.  This means
      that they live inside the method, and they cannot leave.
      If you try, you will get an error:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def doubleThis num
        numTimes2 = num*2
        puts num.to_s+' doubled is '+numTimes2.to_s
      end
      
      doubleThis 44
      puts numTimes2.to_s
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Undefined local variable...  In fact, we <em>did</em>
      define that local variable, but it isn't local to where
      we tried to use it; it's local to the method.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      This might seem inconvenient, but it actually quite nice.
      While it does mean that you have no access to variables
      inside methods, it also means that they have no access
      to <em>your</em> variables, and thus can't screw them up:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def littlePest var
        var = nil
        puts 'HAHA!  I ruined your variable!'
      end
      
      var = 'You can\\'t even touch my variable!'
      littlePest var
      puts var
      END_CODE
    end
    para do <<-END_PARAGRAPH
      There are actually <em>two</em> variables in that little
      program named #{code 'var'}:  one inside #{code 'littlePest'},
      and one outside of it.  When we called #{code 'littlePest var'},
      we really just passed the string from one #{code 'var'} to
      the other, so that both were pointing to the same string.
      Then #{code 'littlePest'} pointed its own <em>local</em>
      #{code 'var'} to #{code 'nil'}, but that did nothing to the
      #{code 'var'} outside the method.
      END_PARAGRAPH
    end
    h2 {'Return Values'}
    para do <<-END_PARAGRAPH
      You may have noticed that some methods give you something
      back when you call them.  For example, #{code 'gets'}
      <dfn>returns</dfn> a string (the string you typed in),
      and the #{code '+'} method in #{code '5+3'}, (which is
      really #{code '5.+(3)'}) returns #{code '8'}.  The
      arithmetic methods for numbers return numbers, and the
      arithmetic methods for strings return strings.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      It's important to understand the difference between methods
      returning a value to where the method was called, and
      your program outputting information to your screen, like
      #{code 'puts'} does.  Notice that #{code '5+3'} returns
      #{code '8'}; it does <strong>not</strong> output
      #{output '8'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So what <em>does</em> #{code 'puts'} return?  We never cared
      before, but let's look at it now:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      returnVal = puts 'This puts returned:'
      puts returnVal
      END_CODE
    end
    para do <<-END_PARAGRAPH
      So the first #{code 'puts'} returned #{code 'nil'}.  Though
      we didn't test it, the second #{code 'puts'} did, too;
      #{code 'puts'} always returns #{code 'nil'}.  Every method
      has to return something, even if it's just #{code 'nil'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Take a quick break and write a program
      to find out what #{code 'sayMoo'} returned.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Were you surprised?  Well, here's how it works:  the value
      returned from a method is simply the last line of the method.  In
      the case of #{code 'sayMoo'}, this means it returns
      #{code "puts 'mooooooo...'*numberOfMoos"}, which is just
      #{code 'nil'} since #{code 'puts'} always returns
      #{code 'nil'}.  If we wanted all of our methods to
      return the string #{code "'yellow submarine'"}, we
      would just need to put <em>that</em> at the end of
      them:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def sayMoo numberOfMoos
        puts 'mooooooo...'*numberOfMoos
        'yellow submarine'
      end
      
      x = sayMoo 2
      puts x
      END_CODE
    end
    para do <<-END_PARAGRAPH
      So, let's try that psychology experiment again,
      but this time we'll write a method to ask the questions for us.
      It will need to take the question as a parameter, and return
      #{code 'true'} if they answered #{input 'yes'} and
      #{code 'false'} if they answered #{input 'no'}.  (Even though
      most of the time we just ignore the answer, it's still a
      good idea for our method to return the answer.  This way we
      can use it for the bed-wetting question, too.)
      I'm also going to shorten the greeting and the debriefing,
      just so this is easier to read:
      END_PARAGRAPH
    end
    prog ['yes','yes','no way!','NO','yes','yes','yes','yes','yes'] do <<-END_CODE
      def ask question
        goodAnswer = false
        while (not goodAnswer)
          puts question
          reply = gets.chomp.downcase
          
          if (reply == 'yes' or reply == 'no')
            goodAnswer = true
            if reply == 'yes'
              answer = true
            else
              answer = false
            end
          else
            puts 'Please answer "yes" or "no".'
          end
        end
        
        answer  #  This is what we return (true or false).
      end
      
      puts 'Hello, and thank you for...'
      puts
      
      ask 'Do you like eating tacos?'      #  We ignore this return value.
      ask 'Do you like eating burritos?'
      wetsBed = ask 'Do you wet the bed?'  #  We save this return value.
      ask 'Do you like eating chimichangas?'
      ask 'Do you like eating sopapillas?'
      ask 'Do you like eating tamales?'
      puts 'Just a few more questions...'
      ask 'Do you like drinking horchata?'
      ask 'Do you like eating flautas?'
      
      puts
      puts 'DEBRIEFING:'
      puts 'Thank you for...'
      puts
      puts wetsBed
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Not bad, huh?  We were able to add more questions (and
      adding questions is <em>easy</em> now), but our program
      is still quite a bit shorter!  It's a big improvement
      &mdash; a lazy programmer's dream.
      END_PARAGRAPH
    end
    h2 {'One More Big Example'}
    para do <<-END_PARAGRAPH
      I think another example method would be helpful here.
      We'll call this one #{code 'englishNumber'}.
      It will take a number, like #{code '22'},
      and return the english version of it (in this case,
      the string #{code "'twenty-two'"}).  For now, let's have it
      only work on integers from #{code '0'} to #{code '100'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      <em>(<strong>NOTE:</strong>  This method uses a new trick
      to return from a method early using the </em>#{code 'return'}<em>
      keyword, and introduces a new twist on branching:
      </em>#{code 'elsif'}<em>.  It should be clear in context
      how these work.)</em>
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def englishNumber number
        #  We only want numbers from 0-100.
        if number < 0
          return 'Please enter a number zero or greater.'
        end
        if number > 100
          return 'Please enter a number 100 or lesser.'
        end
        
        numString = ''  #  This is the string we will return.
        
        #  "left" is how much of the number we still have left to write out.
        #  "write" is the part we are writing out right now.
        #  write and left... get it?  :)
        left  = number
        write = left/100          #  How many hundreds left to write out?
        left  = left - write*100  #  Subtract off those hundreds.
        
        if write > 0
          return 'one hundred'
        end
        
        write = left/10          #  How many tens left to write out?
        left  = left - write*10  #  Subtract off those tens.
        
        if write > 0
          if write == 1  #  Uh-oh...
            #  Since we can't write "tenty-two" instead of "twelve",
            #  we have to make a special exception for these.
            if    left == 0
              numString = numString + 'ten'
            elsif left == 1
              numString = numString + 'eleven'
            elsif left == 2
              numString = numString + 'twelve'
            elsif left == 3
              numString = numString + 'thirteen'
            elsif left == 4
              numString = numString + 'fourteen'
            elsif left == 5
              numString = numString + 'fifteen'
            elsif left == 6
              numString = numString + 'sixteen'
            elsif left == 7
              numString = numString + 'seventeen'
            elsif left == 8
              numString = numString + 'eighteen'
            elsif left == 9
              numString = numString + 'nineteen'
            end
            #  Since we took care of the digit in the ones place already,
            #  we have nothing left to write.
            left = 0
          elsif write == 2
            numString = numString + 'twenty'
          elsif write == 3
            numString = numString + 'thirty'
          elsif write == 4
            numString = numString + 'forty'
          elsif write == 5
            numString = numString + 'fifty'
          elsif write == 6
            numString = numString + 'sixty'
          elsif write == 7
            numString = numString + 'seventy'
          elsif write == 8
            numString = numString + 'eighty'
          elsif write == 9
            numString = numString + 'ninety'
          end
          
          if left > 0
            numString = numString + '-'
          end
        end
        
        write = left  #  How many ones left to write out?
        left  = 0     #  Subtract off those ones.
        
        if write > 0
          if    write == 1
            numString = numString + 'one'
          elsif write == 2
            numString = numString + 'two'
          elsif write == 3
            numString = numString + 'three'
          elsif write == 4
            numString = numString + 'four'
          elsif write == 5
            numString = numString + 'five'
          elsif write == 6
            numString = numString + 'six'
          elsif write == 7
            numString = numString + 'seven'
          elsif write == 8
            numString = numString + 'eight'
          elsif write == 9
            numString = numString + 'nine'
          end
        end
        
        if numString == ''
          #  The only way "numString" could be empty is if
          #  "number" is 0.
          return 'zero'
        end
        
        #  If we got this far, then we had a number somewhere
        #  in between 0 and 100, so we need to return "numString".
        numString
      end
      
      puts englishNumber(  0)
      puts englishNumber(  9)
      puts englishNumber( 10)
      puts englishNumber( 11)
      puts englishNumber( 17)
      puts englishNumber( 32)
      puts englishNumber( 88)
      puts englishNumber( 99)
      puts englishNumber(100)
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Well, there are certainly a few things about this program
      I don't like.  First, it has too much repetition.  Second,
      it doesn't handle numbers greater than 100.  Third, there
      are too many special cases, too many #{code 'return'}s.
      Let's use some arrays and try to clean it up a bit:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def englishNumber number
        if number < 0  #  No negative numbers.
          return 'Please enter a number that isn\\'t negative.'
        end
        if number == 0
          return 'zero'
        end
        
        #  No more special cases!  No more returns!
        
        numString = ''  #  This is the string we will return.
        
        onesPlace = ['one',     'two',       'three',    'four',     'five',
                     'six',     'seven',     'eight',    'nine']
        tensPlace = ['ten',     'twenty',    'thirty',   'forty',    'fifty',
                     'sixty',   'seventy',   'eighty',   'ninety']
        teenagers = ['eleven',  'twelve',    'thirteen', 'fourteen', 'fifteen',
                     'sixteen', 'seventeen', 'eighteen', 'nineteen']
        
        #  "left" is how much of the number we still have left to write out.
        #  "write" is the part we are writing out right now.
        #  write and left... get it?  :)
        left  = number
        write = left/100          #  How many hundreds left to write out?
        left  = left - write*100  #  Subtract off those hundreds.
        
        if write > 0
          #  Now here's a really sly trick:
          hundreds  = englishNumber write
          numString = numString + hundreds + ' hundred'
          #  That's called "recursion".  So what did I just do?
          #  I told this method to call itself, but with "write" instead of
          #  "number".  Remember that "write" is (at the moment) the number of
          #  hundreds we have to write out.  After we add "hundreds" to "numString",
          #  we add the string ' hundred' after it.  So, for example, if
          #  we originally called englishNumber with 1999 (so "number" = 1999),
          #  then at this point "write" would be 19, and "left" would be 99.
          #  The laziest thing to do at this point is to have englishNumber
          #  write out the 'nineteen' for us, then we write out ' hundred',
          #  and then the rest of englishNumber writes out 'ninety-nine'.
          
          if left > 0
            #  So we don't write 'two hundredfifty-one'...
            numString = numString + ' '
          end
        end
        
        write = left/10          #  How many tens left to write out?
        left  = left - write*10  #  Subtract off those tens.
        
        if write > 0
          if ((write == 1) and (left > 0))
            #  Since we can't write "tenty-two" instead of "twelve",
            #  we have to make a special exception for these.
            numString = numString + teenagers[left-1]
            #  The "-1" is because teenagers[3] is 'fourteen', not 'thirteen'.
            
            #  Since we took care of the digit in the ones place already,
            #  we have nothing left to write.
            left = 0
          else
            numString = numString + tensPlace[write-1]
            #  The "-1" is because tensPlace[3] is 'forty', not 'thirty'.
          end
          
          if left > 0
            #  So we don't write 'sixtyfour'...
            numString = numString + '-'
          end
        end
        
        write = left  #  How many ones left to write out?
        left  = 0     #  Subtract off those ones.
        
        if write > 0
          numString = numString + onesPlace[write-1]
          #  The "-1" is because onesPlace[3] is 'four', not 'three'.
        end
        
        #  Now we just return "numString"...
        numString
      end
      
      puts englishNumber(  0)
      puts englishNumber(  9)
      puts englishNumber( 10)
      puts englishNumber( 11)
      puts englishNumber( 17)
      puts englishNumber( 32)
      puts englishNumber( 88)
      puts englishNumber( 99)
      puts englishNumber(100)
      puts englishNumber(101)
      puts englishNumber(234)
      puts englishNumber(3211)
      puts englishNumber(999999)
      puts englishNumber(1000000000000)
      END_CODE
    end
    para do <<-END_PARAGRAPH
      <em>Ahhhh....</em> That's much, much better.  The program is
      fairly dense, which is why I put in so many comments.  It
      even works for large numbers... though not quite as nicely
      as one would hope.  For example, I think #{code "'one trillion'"}
      would be a nicer return value for that last number, or even
      #{code "'one million million'"} (though all three are correct).
      In fact, you can do that right now...
      END_PARAGRAPH
    end
    h2 {'A Few Things to Try'}
    para do <<-END_PARAGRAPH
      &bull; Expand upon #{code 'englishNumber'}.  First, put in
      thousands.  So it should return #{code "'one thousand'"}
      instead of #{code "'ten hundred'"} and #{code "'ten thousand'"}
      instead of #{code "'one hundred hundred'"}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Expand upon #{code 'englishNumber'} some more.
      Now put in millions, so you get #{code "'one million'"}
      instead of #{code "'one thousand thousand'"}.  Then try adding
      billions and trillions.  How high can you go?
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; How about #{code 'weddingNumber'}?  It should
      work almost the same as #{code 'englishNumber'}, except
      that it should insert the word "and" all over the place,
      returning things like #{code "'nineteen hundred and seventy and two'"},
      or however wedding invitations are supposed to look.  I'd give you more
      examples, but I don't fully understand it myself.  You might
      need to contact a wedding coordinator to help you.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; <em>"Ninety-nine bottles of beer..."</em>
      Using #{code 'englishNumber'} and your old program, write out the
      lyrics to this song the <em>right</em> way this time.
      Punish your computer:  have it start at 9999.  (Don't pick
      a number too large, though, because writing all of that to
      the screen takes your computer quite a while.  A hundred
      thousand bottles of beer takes some time; and if you pick
      a million, you'll be punishing yourself as well!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Congratulations!  At this point, you are a true
      programmer!  You have learned
      everything you need to build huge programs from scratch.
      If you have ideas for programs you would like to write
      for yourself, give them a shot!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Of course, building everything from scratch can be a
      pretty slow process.  Why spend time writing code that
      someone else already wrote?  
      Would you like your program to send some email?
      Would you like to save and load files on your computer?
      How about generating web pages for a tutorial where
      the code samples are actually being run every time the
      web page is loaded?  ;) Ruby has many different
      #{makeLink 'kinds of objects', :generateClasses}
      we can use to help us write better programs faster.
      END_PARAGRAPH
    end
  end
  
  #
  #  CLASSES
  #
  
  def generateClasses
    para do <<-END_PARAGRAPH
      So far we've seen several different kinds, or
      <dfn>classes</dfn>, of objects:
      strings, integers, floats, arrays, and a few special objects
      (#{code 'true'}, #{code 'false'}, and #{code 'nil'}) which
      we'll talk about later.
      In Ruby, these classes are always capitalized:  #{code 'String'},
      #{code 'Integer'}, #{code 'Float'}, #{code 'Array'}... etc.
      In general, if we want to create a new object of a
      certain class, we use #{code 'new'}:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      a = Array.new  + [12345]  #  Array  addition.
      b = String.new + 'hello'  #  String addition.
      c = Time.new
      
      puts 'a = '+a.to_s
      puts 'b = '+b.to_s
      puts 'c = '+c.to_s
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Because we can create arrays and strings using
      #{code '[...]'} and #{code "'...'"} respectively, we rarely create
      them using #{code 'new'}.  (Though it's not really obvious
      from the above example, #{code 'String.new'} creates
      an empty string, and #{code 'Array.new'} creates an empty
      array.)  Also, numbers are special exceptions:  you can't
      create an integer with #{code 'Integer.new'}.  You just have
      to write the integer.
      END_PARAGRAPH
    end
    h2 {"The #{code 'Time'} Class"}
    para do <<-END_PARAGRAPH
      So what's the story with this #{code 'Time'} class?
      #{code 'Time'} objects represent moments in time.  You can
      add (or subtract) numbers to (or from) times to get new times:
      adding #{code '1.5'} to a time makes a new time one-and-a-half
      seconds later:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      time  = Time.new   #  The moment you got this web page.
      time2 = time + 60  #  One minute later.
      
      puts time
      puts time2
      END_CODE
    end
    para do <<-END_PARAGRAPH
      You can also make a time for a specific moment using
      #{code 'Time.mktime'}:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      puts Time.mktime(2000, 1, 1)          #  Y2K.
      puts Time.mktime(1976, 8, 3, 10, 11)  #  When I was born.
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Notice:  that's when I was born in Pacific Daylight Savings
      Time (PDT).  When Y2K struck, though, it was Pacific
      Standard Time (PST), at least to us West Coasters.  The
      parentheses are to group the parameters to #{code 'mktime'}
      together.  The more parameters you add, the more accurate your
      time becomes.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      You can compare times using the comparison methods
      (an earlier time is <em>less than</em> a later time),
      and if you subtract one time from another, you'll get the
      number of seconds between them.  Play around with it!
      END_PARAGRAPH
    end
    h2 {'A Few Things to Try'}
    para do <<-END_PARAGRAPH
      &bull; One billion seconds...  Find out the exact second you
      were born (if you can).  Figure out when you will turn (or
      perhaps when you did turn?) one billion seconds old.  Then
      go mark your calendar.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Happy Birthday!  Ask what year a person was born in,
      then the month, then the day.  Figure out how old they are
      and give them a big #{output 'SPANK!'} for each birthday
      they have had.
      END_PARAGRAPH
    end
    h2 {"The #{code 'Hash'} Class"}
    para do <<-END_PARAGRAPH
      Another useful class is the #{code 'Hash'} class.  Hashes
      are a lot like arrays:  they have a bunch of slots which
      can point to various objects.  However, in an array, the
      slots are lined up in a row, and each one is numbered
      (starting from zero).  In a hash, the slots aren't in
      a row (they are just sort of jumbled together), and you
      can use <em>any</em> object to refer to a slot, not just
      a number.  It's good to use hashes when you have a bunch
      of things you want to keep track of, but they don't really
      fit into an ordered list.  For example, the colors I use for different
      parts of the code which created this tutorial:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      colorArray = []  #  same as Array.new
      colorHash  = {}  #  same as Hash.new
      
      colorArray[0]         = '#{@@STRING_COLOR}'
      colorArray[1]         = '#{@@NUMBER_COLOR}'
      colorArray[2]         = '#{@@KEYWORD_COLOR}'
      colorHash['strings']  = '#{@@STRING_COLOR}'
      colorHash['numbers']  = '#{@@NUMBER_COLOR}'
      colorHash['keywords'] = '#{@@KEYWORD_COLOR}'
      
      colorArray.each do |color|
        puts color
      end
      colorHash.each do |codeType, color|
        puts codeType + ':  ' + color
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      If I use an array, I have to remember that slot #{code '0'} is for
      strings, slot #{code '1'} is for numbers, etc.  But if I use a hash, it's
      easy!  Slot #{code "'strings'"} holds the color of the strings, of course.
      Nothing to remember.  You might have noticed that when we used
      #{code 'each'}, the objects in the hash didn't come out in the same
      order we put them in.  (At least, they didn't when I wrote this.
      Maybe they did just now... you never know with hashes.)  Arrays
      are for keeping things in order, not hashes.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Though people usually use strings to name the slots in a hash, you
      could use any kind of object, even arrays and other hashes (though I can't
      think of why you would want to do this...):
      END_PARAGRAPH
    end
    prog false do <<-END_CODE
      weirdHash = Hash.new
      
      weirdHash[12] = 'monkeys'
      weirdHash[[]] = 'emptiness'
      weirdHash[Time.new] = 'no time like the present'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Hashes and arrays are good for different things; it's up
      to you to decide which one is best for a particular problem.
      END_PARAGRAPH
    end
    h2 {'Extending Classes'}
    para do <<-END_PARAGRAPH
      At the end of the last chapter, you wrote a method to give
      the English phrase for a given integer.  It wasn't an integer
      method, though; it was just a generic "program" method.  Wouldn't
      it be nice if you could write something like #{code '22.to_eng'}
      instead of #{code 'englishNumber 22'}?  Here's how you would do
      that:
      END_PARAGRAPH
    end
    #  HACK ALERT!!!  (I can't get to the global namespace transparently
    #                  from inside the StringIO object in a mod_ruby script.)
    integerClassHack = <<-END_CODE
        def to_eng
          if self == 5
            english = 'five'
          else
            english = 'fifty-eight'
          end
          
          english
        end
      END_CODE
    
    Integer.module_eval integerClassHack  #  This is the real method definition.
    #  The following defines a method in "another" integer class:
    #  END HACK ALERT!!!
    prog do <<-END_CODE
      class Integer
        
#{integerClassHack}
      end
      
      #  I'd better test on a couple of numbers...
      puts 5.to_eng
      puts 58.to_eng
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Well, I tested it; it seems to work.  ;)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So we defined an integer method by jumping into the
      #{code 'Integer'} class, defining the method there,
      and jumping back out.  Now all integers have this
      (somewhat incomplete) method.  In fact, if you didn't
      like the way a built-in method like
      #{code 'to_s'} worked, you could just
      redefine it in much the same way... but I don't recommend
      it!  It's best to leave the old methods alone and to
      make new ones when you want to do something new.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So... confused yet?  Let me go over that last program
      some more.  So far, whenever we executed any code or
      defined any methods, we did it in the default
      "program" object.  In our last program, we left that
      object for the first time and went into the class
      #{code 'Integer'}.  We defined a method there (which
      makes it an integer method) and all integers can
      use it.  Inside that method we use #{code 'self'}
      to refer to the object (the integer) using the method.
      END_PARAGRAPH
    end
    h2 {'Creating Classes'}
    para do <<-END_PARAGRAPH
      We've seen a number of different classes of objects.
      However, it's easy to come up with kinds of objects
      that Ruby doesn't have.  Luckily, creating a new
      class is as easy as extending an old one.  Let's say
      we wanted to make some dice in Ruby.  Here's how we
      could make the Die class:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      class Die
        
        def roll
          1 + rand(6)
        end
        
      end
      
      #  Let's make a couple of dice...
      dice = [Die.new, Die.new]
      
      #  ...and roll them.
      dice.each do |die|
        puts die.roll
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      (If you skipped the section on random numbers,
      #{code 'rand(6)'} just gives a random number between
      #{code '0'} and #{code '5'}.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      And that's it!  Objects of our very own.  Roll the dice
      a few times (with your reload button) and watch what
      turns up.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      We can define
      all sorts of methods for our objects... but there's
      something missing.  Working with these objects feels
      a lot like programming before we learned about
      variables.  Look at our dice, for example.  We can
      roll them, and each time we do they give us a different
      number.  But if we wanted to hang on to that number, we
      would have to create a variable to point to the number.
      It seems like any decent die should be able to <em>have</em>
      a number, and that rolling the die should change the number.
      If we keep track of the die, we shouldn't also have to keep track
      of the number it is showing.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      However, if we try to store the number we rolled in a (local)
      variable in #{code 'roll'}, it will be gone as soon as
      #{code 'roll'} is finished.  We need to store the number in
      a different kind of variable:
      END_PARAGRAPH
    end
    h2 {'Instance Variables'}
    para do <<-END_PARAGRAPH
      Normally when we want to talk about a string, we will just
      call it a <dfn>string</dfn>.  However, we could also call
      it a <dfn>string object</dfn>.  Sometimes programmers might
      call it <dfn>an instance of the class #{code 'String'}</dfn>, but this
      is just a fancy (and rather long-winded) way of saying
      <dfn>string</dfn>.  An <dfn>instance</dfn> of a class is just an
      object of that class.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So instance variables are just an object's variables.  A
      method's local variables last until the method is finished.
      An object's instance variables, on the other hand, will
      last as long as the object does.  To tell instance variables
      from local variables, they have #{code '@'} in front of
      their names:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      class Die
        
        def roll
          @numberShowing = 1 + rand(6)
        end
        
        def showing
          @numberShowing
        end
        
      end
      
      die = Die.new
      die.roll
      puts die.showing
      puts die.showing
      die.roll
      puts die.showing
      puts die.showing
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Very nice!  So #{code 'roll'} rolls the die and
      #{code 'showing'} tells us which number is showing.
      However, what if we try to look at what's showing before
      we've rolled the die (before we've set #{code '@numberShowing'})?
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      class Die
        
        def roll
          @numberShowing = 1 + rand(6)
        end
        
        def showing
          @numberShowing
        end
        
      end
      
      #  Since I'm not going to use this die again,
      #  I don't need to save it in a variable.
      puts Die.new.showing
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Hmmm... well, at least it didn't give us an error.  Still,
      it doesn't really make sense for a die to be "unrolled", or
      whatever #{output 'nil'} is supposed to mean here.  It would
      be nice if we could set up our new die object right when it's
      created.  That's what #{code 'initialize'} is for:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      class Die
        
        def initialize
          #  I'll just roll the die, though we
          #  could do something else if we wanted
          #  to, like setting the die with 6 showing.
          roll
        end
        
        def roll
          @numberShowing = 1 + rand(6)
        end
        
        def showing
          @numberShowing
        end
        
      end
      
      puts Die.new.showing
      END_CODE
    end
    para do <<-END_PARAGRAPH
      When an object is created, its #{code 'initialize'}
      method (if it has one defined) is always called.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Our dice are just about perfect.  The only thing that
      might be missing is a way to set which side of a die
      is showing... why don't you write a #{code 'cheat'}
      method which does just that!  Come back when you're
      done (and when you tested that it worked, of course).
      Make sure that someone can't set the die to have a
      #{code '7'} showing!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      So that's some pretty cool stuff we just covered.  It's tricky,
      though, so let me give another, more interesting example.
      Let's say we want to make a simple virtual pet, a baby
      dragon.  Like most babies, it should be able to eat, sleep,
      and poop, which means we will need to be able to feed it,
      put it to bed, and take it on walks.  Internally, our dragon
      will need to keep track of if it is hungry, tired, or needs
      to go, but we won't be able to see that when we interact
      with our dragon, just like you can't ask a human baby,
      "Are you hungry?".  We'll also add a few other fun ways
      we can interact with our baby dragon, and when he is born
      we'll give him a name.  (Whatever you pass into the
      #{code 'new'} method is passed into the #{code 'initialize'}
      method for you.)  Alright, let's give it a shot:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      class Dragon
        
        def initialize name
          @name = name
          @asleep = false
          @stuffInBelly     = 10  #  He's full.
          @stuffInIntestine =  0  #  He doesn't need to go.
          
          puts @name + ' is born.'
        end
        
        def feed
          puts 'You feed ' + @name + '.'
          @stuffInBelly = 10
          passageOfTime
        end
        
        def walk
          puts 'You walk ' + @name + '.'
          @stuffInIntestine = 0
          passageOfTime
        end
        
        def putToBed
          puts 'You put ' + @name + ' to bed.'
          @asleep = true
          3.times do
            if @asleep
              passageOfTime
            end
            if @asleep
              puts @name + ' snores, filling the room with smoke.'
            end
          end
          if @asleep
            @asleep = false
            puts @name + ' wakes up slowly.'
          end
        end
        
        def toss
          puts 'You toss ' + @name + ' up into the air.'
          puts 'He giggles, which singes your eyebrows.'
          passageOfTime
        end
        
        def rock
          puts 'You rock ' + @name + ' gently.'
          @asleep = true
          puts 'He briefly dozes off...'
          passageOfTime
          if @asleep
            @asleep = false
            puts '...but wakes when you stop.'
          end
        end
        
        private
        
        #  "private" means that the methods defined here are
        #  methods internal to the object.  (You can feed
        #  your dragon, but you can't ask him if he's hungry.)
        
        def hungry?
          #  Method names can end with "?".
          #  Usually, we only do this if the method
          #  returns true or false, like this:
          @stuffInBelly <= 2
        end
        
        def poopy?
          @stuffInIntestine >= 8
        end
        
        def passageOfTime
          if @stuffInBelly > 0
            #  Move food from belly to intestine.
            @stuffInBelly     = @stuffInBelly     - 1
            @stuffInIntestine = @stuffInIntestine + 1
          else  #  Our dragon is starving!
            if @asleep
              @asleep = false
              puts 'He wakes up suddenly!'
            end
            puts @name + ' is starving!  In desperation, he ate YOU!'
            exit  #  This quits the program.
          end
          
          if @stuffInIntestine >= 10
            @stuffInIntestine = 0
            puts 'Whoops!  ' + @name + ' had an accident...'
          end
          
          if hungry?
            if @asleep
              @asleep = false
              puts 'He wakes up suddenly!'
            end
            puts @name + '\\'s stomach grumbles...'
          end
          
          if poopy?
            if @asleep
              @asleep = false
              puts 'He wakes up suddenly!'
            end
            puts @name + ' does the potty dance...'
          end
        end
        
      end
      
      pet = Dragon.new 'Norbert'
      pet.feed
      pet.toss
      pet.walk
      pet.putToBed
      pet.rock
      pet.putToBed
      pet.putToBed
      pet.putToBed
      pet.putToBed
      END_CODE
    end
    para do <<-END_PARAGRAPH
      <em>Whew!</em>  Of course, it would be nicer if this was
      an interactive program, but you can do that part later.
      I was just trying to show the parts directly relating to
      creating a new dragon class.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      We saw a few new things in that example.  The first is
      simple:  #{code 'exit'} terminates the program right
      then and there.  The second is the word #{code 'private'}
      which we stuck right in the middle of our class definition.
      I could have left it out, but I wanted to enforce the idea
      of certain methods being things you can do to a dragon, and
      others which simply happen within the dragon.  You can think
      of these as being "under the hood":  unless you are an
      automobile mechanic, all you really need to know is the gas
      pedal, the brake pedal, and the steering wheel.  A programmer
      might call those the <dfn>public interface</dfn> to your car.
      How your airbag knows when to deploy, however, is internal to
      the car; the typical user (driver) doesn't need to know about
      this.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Actually, for a bit more concrete example along those lines,
      let's talk about how you might represent a car in a video
      game (which happens to be my line of work).  First, you would
      want to decide what you want your public interface to look like;
      in other words, which methods should people be able to call on
      one of your car objects?  Well, they need to be able to push
      the gas pedal and the brake pedal, but they would also need to
      be able to specify how hard they are pushing the pedal.  (There's
      a big difference between flooring it and tapping it.)  They would
      also need to be able to steer, and again, they would need to be
      able to say how hard they are turning the wheel.  I suppose you
      could go further and add a clutch, turn signals, rocket launcher,
      afterburner, flux capacitor, etc... it depends
      on what type of game you are making.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Internal to a car object, though, there would need to be much
      more going on; other things a car would need are a speed,
      a direction, and a position (at the most basic).  These attributes
      would be modified by pressing on the gas or brake pedals and
      turning the wheel, of course, but the user would not be able
      to set the position directly (which would be like warping).
      You might also want to keep track of skidding or damage, if
      you have caught any air, and so on.  These would all be internal
      to your car object.
      END_PARAGRAPH
    end
    h2 {'A Few Things to Try'}
    para do <<-END_PARAGRAPH
      &bull; Make an #{code 'OrangeTree'} class.  It should have a
      #{code 'height'} method which returns its height, and a
      #{code 'oneYearPasses'} method, which, when called, ages the tree
      one year.  Each year the tree grows taller (however much you think
      an orange tree should grow in a year), and after some number of
      years (again, your call) the tree should die.  For the first few
      years, it should not produce fruit, but after a while it should,
      and I guess that older trees produce more each year than younger
      trees... whatever you think makes most sense.  And, of course,
      you should be able to #{code 'countTheOranges'} (which returns
      the number of oranges on the tree), and #{code 'pickAnOrange'}
      (which reduces the #{code '@orangeCount'} by one and returns a
      string telling you how delicious the orange was, or else it just
      tells you that there are no more oranges to pick this year).
      Make sure that any oranges you don't pick one year fall off
      before the next year.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; Write a program so that you can interact with your
      baby dragon.  You should be able to enter commands like
      #{input 'feed'} and #{input 'walk'}, and have those methods
      be called on your dragon.  Of course, since what you are
      inputting are just strings, you will have to have some sort
      of <dfn>method dispatch</dfn>, where your program checks
      which string was entered, and then calls the appropriate method.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      And that's just about all there is to it!  But wait a second...
      I haven't told you about any of those classes for doing things
      like sending an email, or saving and loading files on your
      computer, or how to create windows and buttons, or 3D worlds,
      or anything!  Well, there are just <em>so many</em> classes
      you can use that I can't possibly show you them all; I don't
      even know what most of them are!  What I <em>can</em> tell
      you is where to find out more about them, so you can learn
      about the ones you want to program with.  Before I send you
      off, though, there is just one more feature of Ruby you should
      know about, something most languages don't have, but which I
      simply could not live without:
      #{makeLink 'blocks and procs', :generateBlocksProcs}.
      END_PARAGRAPH
    end

  end
  
  #
  #  BLOCKS AND PROCS
  #
  
  def generateBlocksProcs
    para do <<-END_PARAGRAPH
      Esta es definitivamente una de las mejores herramientas de Ruby.
      Algunos lenguajes tienen esta herramienta, pienso que la llamaran
      de otra forma(como <dfn>closures</dfn>), pero la mayoría de los mas
      populares no lo hacen, una pena.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Entonces que es esto que es tan bueno? Esto tiene la habilidad
      de tomar un <dfn>bloque</dfn> de código(código entre #{code 'do'} 
      y #{code 'end'}), que rodean esto en un objeto (llamado <dfn>proc</dfn>),
      lo guarda en una variable o lo pasa a un método, y ejecuta el código en un
      bloque donde te guste(mas de una vez, si quieres.) Entonces esto es 
      un tipo método en si mismo, excepto que no es compartido con otro objeto mas
      (esto <em>es</em> un objeto), y puedes almacenar o pasar este como cualquier 
      otro objeto. Es tiempo de un ejemplo:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      toast = Proc.new do
        puts 'Aplausos!'
      end
      
      toast.call
      toast.call
      toast.call
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Entonces creé un proc (el cual pienzo debería ser pronunciado como
      "procedimiento", pero mas importante, esto rima con "bloque") el cual
      contiene un bloque de código, y #{code 'call'}ed ('llame') el proc tres
      veces. Como puedes ver, esto es como un método.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      En realidad, esto es mas que métodos que he mostrado, porque los bloques pueden
      tomar parametros:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      doYouLike = Proc.new do |aGoodThing|
        puts 'I *really* like '+aGoodThing+'!'
      end
      
      doYouLike.call 'chocolate'
      doYouLike.call 'ruby'
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Muy bien, entonces vemos que son los bloques y procs, y como usarlos, pero 
      cual es el punto? Porque no utilizar simples métodos? Bueno, esto es porque
      hay mas cosas que no podemos hacer con simples métodos. En particular, no 
      puedes pasar métodos a otros métodos(pero puedes pasar procs dentro de métodos),
      y métodos no pueden retornar otros métodos(pero ellos pueden retornar procs). Esto
      es simplemente porque procs son objetos; los métodos no son objetos
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      (De hecho, es algo familiar para ti? Sí, tu has visto bloques antes.. cuando aprendiste
       sobre iteradores. Pero vamos a hablar un poco mas acerca de esto en breve)	
      END_PARAGRAPH
    end
    h2 { 'Methods Which Take Procs' }
    para do <<-END_PARAGRAPH
      Cuando pasamos un proc en un un metodo, podemos controlar como, o cuantas veces llamamos
      el proc. Por ejemplo, vamos a decir que queremos hacer antes y después que cierto código
      se esta ejecutando:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def doSelfImportantly someProc
        puts 'Everybody just HOLD ON!  I have something to do...'
        someProc.call
        puts 'Ok everyone, I\\'m done.  Go on with what you were doing.'
      end
      
      sayHello = Proc.new do
        puts 'hello'
      end
      
      sayGoodbye = Proc.new do
        puts 'goodbye'
      end
      
      doSelfImportantly sayHello
      doSelfImportantly sayGoodbye
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Quizás esto no parezca muy fabulozo... pero lo es. :-)
      Es común en programacion tener requerimientos estrictos acerca de 
      que debe ser hecho y cuando. Si quieres salvar un archivo, por ejemplo,
      tienes que abrir el archivo, escribir la informacion que quieres que 
      contenga este, y luego cerrar el archivo. Si olvidas cerrar el archivo, 
      Puede Tener malas consecuencias. Pero cada vez que quieras salvar un archivo
      o cargar uno, tu tienes que hacer lo mismo: abrir el archivo, hacer lo que
      <em>realmente</em> quieres hacer , luego cerrar el archivo. Esto es tedioso
      y facil de olvidar. En Ruby, guardando (o cargando) archivos trabaja similar
      al codigo anterior, entonces no tienes que preocuparte por nada mas que por
      lo que quieres guardar(o subir). (En el próximo capitulo mostrare donde 
      encontrar info sobre guardar y cargar archivos.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      También pudes escribir metodos los cuales cuantas veces, o incluso <em>sí</em>
      llamar a un proc. Aquí hay un metodo el cual llama a un proc pasado en la mitad
      de tiempo, y otro el cual sera llamara a este dos veces:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def maybeDo someProc
        if rand(2) == 0
          someProc.call
        end
      end
      
      def twiceDo someProc
        someProc.call
        someProc.call
      end
      
      wink = Proc.new do
        puts '<wink>'
      end
      
      glance = Proc.new do
        puts '<glance>'
      end
      
      maybeDo wink
      maybeDo glance
      twiceDo wink
      twiceDo glance
      END_CODE
    end
    para do <<-END_PARAGRAPH
      (Si recargas esta pagina un par de veces, veras que la salida cambiara.) Estos son
      algunos de los casos comunes de uso de procs lo que le permite hacer cosas utilizando
      simplemente metodos no podriamos hacerlo. Seguramente, podrías escribir un metodo para
      hacer algo dos veces, pero no podías escribir uno que haga <em>algo</em> dos veces!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Antes de continuar, vamos a ver un último ejemplo. Los procs que 
      hemos visto son bastante similares. Es tiempo de ver algo diferente, 
      entonces vamos a ver cuanto un metodo depende de un proc pasado a este.
      Nuestro metodo tomara algun objeto y un proc, y llamara a este proc 
      sobre este objeto. Si el proc retorna falso, finalizamos; en otro caso
      llamaremos al proc con el objeto. Continuaremos haciendo esto hasta
      que el proc retorne falso(esto es mejor, o el programa finalizara con 
      error). El metodo retornara el último valor no falso retornado por 
      el proc.
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def doUntilFalse firstInput, someProc
        input  = firstInput
        output = firstInput
        
        while output
          input  = output
          output = someProc.call input
        end
        
        input
      end
      
      buildArrayOfSquares = Proc.new do |array|
        lastNumber = array.last
        if lastNumber <= 0
          false
        else
          array.pop                         #  Quitar el último número...
          array.push lastNumber*lastNumber  #  ...y reemplazar este con el último número elevado al cuadrado...
          array.push lastNumber-1           #  ...seguido por un número menor.
        end
      end
      
      alwaysFalse = Proc.new do |justIgnoreMe|
        false
      end
      
      puts doUntilFalse([5], buildArrayOfSquares).inspect
      puts doUntilFalse('Estoy escribiendo esto a las 3:00 am; alguien que lo finalize!', alwaysFalse)
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Esta bien, este es un ejemplo bastante raro, debo admitirlo. Pero esto mustra como 
      actua diferente nuetro metodo cuando le damos diferentes procs.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      The #{code 'inspect'} method is a lot like #{code 'to_s'}, except
      that the string it returns tries to show you the ruby code for
      building the object you passed it.  Here it shows us the whole
      array returned by our first call to #{code 'doUntilFalse'}.  Also, you might
      notice that we never actually squared that #{code '0'} on the end of that
      array, but since #{code '0'} squared is still just #{code '0'}, we didn't have to.
      And since #{code 'alwaysFalse'} was, you know, always #{code 'false'},
      #{code 'doUntilFalse'} didn't do anything at all the second time we
      called it; it just returned what was passed in.
      END_PARAGRAPH
    end
    h2 { 'Methods Which Return Procs' }
    para do <<-END_PARAGRAPH
      One of the other cool things you can do with procs is to create
      them in methods and return them.  This allows all sorts of crazy
      programming power (things with impressive names, like
      <dfn>lazy evaluation</dfn>, <dfn>infinite data structures</dfn>,
      and <dfn>currying</dfn>),
      but the fact is that I almost never do this in practice, nor
      can I remember seeing anyone else do this in their code.  I think
      it's the kind of thing you don't usually end up having to do in Ruby,
      or maybe Ruby just encourages you to find other solutions; I don't
      know.  In any case, I will only touch on this briefly.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      In this example, #{code 'compose'} takes two procs and returns a new
      proc which, when called, calls the first proc and passes its result
      into the second proc.
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def compose proc1, proc2
        Proc.new do |x|
          proc2.call(proc1.call(x))
        end
      end
      
      squareIt = Proc.new do |x|
        x * x
      end
      
      doubleIt = Proc.new do |x|
        x + x
      end
      
      doubleThenSquare = compose doubleIt, squareIt
      squareThenDouble = compose squareIt, doubleIt
      
      puts doubleThenSquare.call(5)
      puts squareThenDouble.call(5)
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Notice that the call to #{code 'proc1'} had to be inside the
      parentheses for #{code 'proc2'} in order for it to be done first.
      END_PARAGRAPH
    end
    h2 { 'Passing Blocks (Not Procs) into Methods' }
    para do <<-END_PARAGRAPH
      Ok, so this has been sort of academically interesting, but also
      sort of a hassle to use.  A lot of the problem is that there are
      three steps you have to go through (defining the method, making
      the proc, and calling the method with the proc), when it sort of
      feels like there should only be two (defining the method, and
      passing the <em>block</em> right into the method, without using
      a proc at all), since most of the time you don't want to use the
      proc/block after you pass it into the method.  Well, wouldn't you
      know, Ruby has it all figured out for us!  In fact, you've already
      been doing it every time you use iterators.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      I'll show you a quick example first, then we'll talk about it.
      END_PARAGRAPH
    end
    #  HACK ALERT!!!  (I can't get to the global namespace transparently
    #                  from inside the StringIO object in a mod_ruby script.)
    arrayClassHack = <<-END_CODE
        def eachEven(&wasABlock_nowAProc)
          isEven = true  #  We start with "true" because arrays start with 0, which is even.
          
          self.each do |object|
            if isEven
              wasABlock_nowAProc.call object
            end
            
            isEven = (not isEven)  #  Toggle from even to odd, or odd to even.
          end
        end
      END_CODE
    
    Array.module_eval arrayClassHack  #  This is the real method definition.
    #  The following defines a method in "another" array class:
    #  END HACK ALERT!!!
    prog do <<-END_CODE
      class Array
        
#{arrayClassHack}
      end
      
      ['apple', 'bad apple', 'cherry', 'durian'].eachEven do |fruit|
        puts 'Yum!  I just love '+fruit+' pies, don\\'t you?'
      end
      
      #  Remember, we are getting the even-numbered elements
      #  of the array, all of which happen to be odd numbers,
      #  just because I like to cause problems like that.
      [1, 2, 3, 4, 5].eachEven do |oddBall|
        puts oddBall.to_s+' is NOT an even number!'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      So to pass in a block to #{code 'eachEven'}, all we had to do was stick
      the block after the method.  You can pass a block into any method this
      way, though many methods will just ignore the block.  In order to make
      your method <em>not</em> ignore the block, but grab it and turn it into
      a proc, put the name of the proc at the end of your method's parameter
      list, preceded by an ampersand (#{code '&'}).  So that part is a little
      tricky, but not too bad, and you only have to do that once (when you
      define the method).  Then you can use the method over and over again,
      just like the built-in methods which take blocks, like #{code 'each'}
      and #{code 'times'}.  (Remember #{code '5.times do'}...?)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      If you get confused, just remember what #{code 'eachEven'} is supposed to do:  call
      the block passed in with every other element in the array.  Once
      you've written it and it works, you don't need to think about what it's
      actually doing under the hood ("which block is called when??"); in
      fact, that's exactly <em>why</em> we write methods like this:  so we
      never have to think about how they work again.  We just use them.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      I remember one time I wanted to be able to time how long different
      sections of a program were taking.  (This is also known as
      <dfn>profiling</dfn> the code.)  So I wrote a method which takes
      the time before running the code, then it runs it, then it takes
      the time again at the end and figures out the difference.  I can't
      find the code right now, but I don't need it; it probably
      went something like this:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def profile descriptionOfBlock, &block
        startTime = Time.now
        
        block.call
        
        duration = Time.now - startTime
        
        puts descriptionOfBlock+':  '+duration.to_s+' seconds'
      end
      
      profile '25000 doublings' do
        number = 1
        
        25000.times do
          number = number + number
        end
        
        puts number.to_s.length.to_s+' digits'  #  That is, the number of digits in this HUGE number.
      end
      
      profile 'count to a million' do
        number = 0
        
        1000000.times do
          number = number + 1
        end
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      How simple!  How elegant!  With that tiny method,
      I can now easily time any section of any program that I want to; I
      just throw the code in a block and send it to #{code 'profile'}.
      What could be simpler?  In most languages, I would have to explicitly
      add that timing code (the stuff in #{code 'profile'}) around every
      section which I wanted to time.  In Ruby, however, I get to keep it
      all in one place, and (more importantly) out of my way!
      END_PARAGRAPH
    end
    h2 {'A Few Things to Try'}
    para do <<-END_PARAGRAPH
      &bull; <em>Grandfather Clock</em>.  Write a method which takes a block
      and calls it once for each hour that has passed today.  That way, if I
      were to pass in the block #{code "do puts 'DONG!' end"}, it would chime
      (sort of) like a grandfather clock.  Test your method
      out with a few different blocks (including the one I just gave you).
      <em><strong>Hint:</strong>  You can use
      </em>#{code 'Time.now.hour'}<em> to get the current hour.
      However, this returns a number between </em>#{code '0'}<em> and </em>#{code '23'}<em>,
      so you will have to alter those numbers in order to get ordinary clock-face
      numbers (</em>#{code '1'}<em> to </em>#{code '12'}<em>).</em>
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      &bull; <em>Program Logger</em>.  Write a method called #{code 'log'}, which
      takes a string description of a block and, of course, a block.  Similar to
      #{code 'doSelfImportantly'}, it should #{code 'puts'} a string telling
      that it has started the block, and another string at the end telling you
      that it has finished the block, and also telling you what the block returned.
      Test your method by sending it a code block.  Inside the block, put <em>another</em>
      call to #{code 'log'}, passing another block to it.  (This is called
      <dfn>nesting</dfn>.)  In other words, your output should look something like this:
      END_PARAGRAPH
    end
    puts '<pre class="L2PoutputBlock">' +
          'Beginning "outer block"...' + $/ +
          'Beginning "some little block"...' + $/ +
          '..."some little block" finished, returning:  5' + $/ +
          'Beginning "yet another block"...' + $/ +
          '..."yet another block" finished, returning:  I like Thai food!' + $/ +
          '..."outer block" finished, returning:  false' + $/ +
          '</pre>'
    para do <<-END_PARAGRAPH
      &bull; <em>Better Logger</em>.  The output from that last logger was kind
      of hard to read, and it would just get worse the more you used it.  It would
      be so much easier to read if it indented the lines in the inner blocks.  To
      do this, you'll need to keep track of how deeply nested you are every time
      the logger wants to write something.  To do this, use a <dfn>global variable</dfn>,
      a variable you can see from anywhere in your code.  To make a global variable,
      just precede your variable name with #{code '$'}, like these:
      #{code '$global'}, #{code '$nestingDepth'}, and #{code '$bigTopPeeWee'}.
      In the end, your logger should output code like this:
      END_PARAGRAPH
    end
    puts '<pre class="L2PoutputBlock">' +
          'Beginning "outer block"...' + $/ +
          '  Beginning "some little block"...' + $/ +
          '    Beginning "teeny-tiny block"...' + $/ +
          '    ..."teeny-tiny block" finished, returning:  lots of love' + $/ +
          '  ..."some little block" finished, returning:  42' + $/ +
          '  Beginning "yet another block"...' + $/ +
          '  ..."yet another block" finished, returning:  I love Indian food!' + $/ +
          '..."outer block" finished, returning:  true' + $/ +
          '</pre>'
    para do <<-END_PARAGRAPH
      Well, that's about all you're going to learn from this tutorial.
      Congratulations!  You've learned a <em>lot</em>!  Maybe you don't feel
      like you remember everything, or you skipped over some parts... really,
      that's just fine.  Programming isn't about what you know; it's about
      what you can figure out.  As long as you know where to find out the
      things you forgot, you're doing just fine.  I hope you don't think
      that I wrote all of this without looking things up every other minute!
      Because I did.  I also got a lot of help with the code which runs all
      of the examples in this tutorial.  But where was <em>I</em> looking
      stuff up, and who was <em>I</em> asking for help?
      #{makeLink 'Let me show you...', :generateBeyond}
      END_PARAGRAPH
    end
  end
  
  #
  #  BEYOND THIS TUTORIAL
  #
  
  def generateBeyond
    para do <<-END_PARAGRAPH
      Entonces que haremos ahora? Si tienes una pregunta, a quien consultarías?
      Que pasa si quieres un programa que abra una página web, envíe un email,
      o redefina el tamaño de una foto digital? Bueno, hay muchos, muchos lugares 
      donde encontrar ayuda Ruby. Desafortunadamente, esto es de poca ayuda, no? :-)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Para mí, hay realmente solo tres lugares donde busco por ayuda sobre Ruby.
      Si es una pequeña pregunta, y pienso que puedo experimentar yo mismo para 
      encontrar la respuesta, utilizo <dfn>irb</dfn>. Si es una gran pregunta,
      busco por esto dentro de mis <dfn>herramientas</dfn>. Y si no puedo darme
      cuenta por mi mismo, entonces pregunto por ayuda en <dfn>ruby-talk</dfn>.
      END_PARAGRAPH
    end
    h2 {'IRB:  Ruby Interactivo'}
    para do <<-END_PARAGRAPH
      Si instalaste Ruby, entonces tienes instalado irb. Para usarlo, solo
      ve a consola y tipea #{input 'irb'}.  Cuando estes en irb, puedes tipear cualquier
      expresion ruby que quieras, y este te dira el valor de esto. Tipea #{input '1 + 2'},
      y este te devolverá #{output '3'}. (Puedes darte cuenta que no tienes que utilizar
      #{code 'puts'}.) Esto es como una calculadora Ruby gigante. Cuando finalizes, solo
      debes tipear #{input 'exit'}.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Hay un montón de cosas ademas para irb, pero puedes aprender mucho más
      probando esto.
      END_PARAGRAPH
    end
    h2 {'The Pickaxe:  "Programming Ruby"'}
    para do <<-END_PARAGRAPH
      Absolutamente <em>el</em> libro Ruby a tener es "Programming Ruby,
      The Pragmatic Programmer's Guide", by David Thomas and Andrew
      Hunt (the Pragmatic Programmers). Mientras que recomiendo tomar la 
      <a href="http://www.pragmaticprogrammer.com/titles/ruby/">segunda edición</a>
      de este excelente libro, con todo lo último cubierto,
      también puedes obtener una versión un poquito más
      antigua (pero interesante también) gratis que esta online. (En realidad,
      si instalaste la versión Windos de Ruby, ya lo tienes.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Puedes encontrar todo lo que necesites de Ruby, desde lo básico a lo
      avanzado, en este libro. Es fácil de leer; fácil de entender; es perfecto.
      Desearía que cada lenguage tuviera un libro de esta calidad. Al reverso
      del libro, encontrarás una gran sección detallando cada método en cada
      clase, explicandolo y dando ejemplos. Me encanta este libro!
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Hay algunos lugares donde puedes conseguirlo(incluyendo
      el sitio mismo  Pragmatic Programmers), pero mi lugar favorito es
      en <a href="http://www.ruby-doc.org/docs/ProgrammingRuby/">ruby-doc.org</a>.
      Esta versión tiene una linda tabla de contenidos a un costado, como también
      un índice. (ruby-doc.org tiene un montón más de grandiosos contenidos también,
      como para el Core API y biblioteca estandar(Standard Library)... basicamente,
      este documenta todo Ruby. <a href="http://www.ruby-doc.org/">Chequealo aquí.</a>)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Y porque es llamado "el pico"? Bueno, hay una imágen de un pico en la tapa del 
      libro. Es un nombre tonto, creo yo, pero quedo así.
      END_PARAGRAPH
    end
    h2 {'Ruby-Talk:  la lista de mails Ruby'}
    para do <<-END_PARAGRAPH
      Aun teniendo irb y el pico, algunas veces sigues sin resolver
      algo que necesitas. O quizás quieres saber si alguien ya hizo algo de lo
      tu estas intentando, para saber si puedes usar eso en cambio. En estos casos
      , el lugar para esto es ruby-talk, la lista de mails Ruby. Esta llendo de gente
      amigable, inteligente y con ganas de ayudar. Para aprender mas de esto, o suscribirte
      , mira <a href="http://www.ruby-lang.org/en/20020104.html">aquí</a>.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      <strong>ADVERTENCIA:</strong> Hay <em>muchos</em> emails en 
      esta lista de correos cada día. Tuve que enviar directamente estos
      a diferentes carpetas de mail para que no me molesten. Si no quieres
      ocuparte de todos esos emails, pienso, no debes inscribirte. La lista
      de mails es espejada en el grupo de noticias comp.lang.ruby, y viceversa,
      entonces puedes ver los mensajes ahí. De igual manera, ves los mismos 
      mensajes, pero en un formato diferente.
      END_PARAGRAPH
    end
    h2 {'Tim Toady'}
    para do <<-END_PARAGRAPH
      Algo que traté de mostrarte, lo cual seguramente podras probar pronto
      , es el concepto de TMTOWTDI (pronunciado como "Tim Toady"): Hay más de
      una forma para hacer esto.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Ahora te voy a decir porque es tan maravilloso TMTOWTDI, mientras 
      otros se sienten diferente con respecto a esto. Realmente no tengo 
      fuertes sentimientos acerca de esto en general, pero pienzo que es 
      una forma <em>terrible</em> de enseñar a alguién de como programar. 
      (Como si aprender a programar de una forma no fuera suficiente desafio y confuso!)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Sin embargo, ahora que estan moviendose más alla de este tutorial, veras mucha
      más diversidad de código. Por ejemplo, pienso que al menos hay otras cinco formas
      de hacer un string(aparte de las que encierran un texto en comillas), y cada uno de estos
      trabaja un poco diferente. Solo mostre lo simple. 
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Cuando hablamos de ramificación, mostré el #{code 'if'},
      pero no mostre el #{code 'unless'}. Voy a dejar que te des 
      cuenta por ti mismo en irb de que se trata.
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      Otro lindo atajo que puedes usar con #{code 'if'},
      #{code 'unless'}, y #{code 'while'}, es esta linda versión de una linea:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      #  Estas lineas son de un programa que escribi para generar 
      #  English
      puts 'grobably combergearl kitatently thememberate' if 5 == 2**2 + 1**1
      puts 'enlestrationshifter supposine follutify blace' unless 'Chris'.length == 5
      END_CODE
    end
    para do <<-END_PARAGRAPH
      Y finalmente, hay otro camino para escribir métodos el que toma bloques
      (no procs). Vimos la parte donde tomabamos el bloque y lo convertíamos 
      dentro de un proc usando el truco #{code '&block'} en la lista de parametros
      cuando defines una función. Entonces, para llamar el bloque, solo usas 
      #{code 'block.call'}.  Bueno, hay una manera más corta(personalmente pienso que 
      es más confuso). Antes que esto:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def doItTwice(&block)
        block.call
        block.call
      end
      
      doItTwice do
        puts 'murditivent flavitemphan siresent litics'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      ...you do this:
      END_PARAGRAPH
    end
    prog do <<-END_CODE
      def doItTwice
        yield
        yield
      end
      
      doItTwice do
        puts 'buritiate mustripe lablic acticise'
      end
      END_CODE
    end
    para do <<-END_PARAGRAPH
      No se... que pienzas? Quizás solo sea yo, pero... #{code 'yield'}?! 
      Si esto fue algo como  #{code 'call_the_hidden_block'} o otra cosa más,
      esto tendría mucho más sentido para mi. Mucha gente dice que #{code 'yield'} 
      tiene sentido para ellos. Pero, supongo que es algo como TMTOWTDI(Hay más de
      una forma para hacer esto.), y eso es todo : ellos hacen las cosas a su manera, 
      y yo lo hare a mi manera.
      END_PARAGRAPH
    end
    h2 {'Fin'}
    para do <<-END_PARAGRAPHi
      Use esto para el bien y no lo malo. :-)  Y si encuentras este tutorial
      útil (o confuso, o si encuentras un error),
      END_PARAGRAPH
    end

  end
  
  
  #  menu helpers
  
  def menuBookLink
    para(:class=>'funnyMenuText fancyMenuText', :style=>'font-size: 12px; font-family: times, serif;') { 'the' }
    para(:class=>'funnyMenuText fancyMenuText', :style=>'font-size: 12px; font-family: times, serif;') { '<em>improved</em>' }
    para(:class=>'funnyMenuText fancyMenuText', :style=>'font-size: 12px; font-family: times, serif; letter-spacing: 6px; font-variant: small-caps;') { 'expanded' }
    para(:class=>'funnyMenuText fancyMenuText', :style=>'font-size: 12px; font-family: times, serif;') { 'version' }
    puts "<a href=\"#{FRLTP_ADDR}\">"
      img(:width=>'100', :height=>'120', :src=>'/images/LTP_cover.jpg')
    puts '</a>'
  end
  
  def menuTOC
    para(:class=>'funnyMenuText') { '&laquo; the original tutorial &raquo;' }
    
    ol(:start=>'0', :style=>'padding-top: 15px; padding-bottom: 15px;') do
      @chapters.sort_by{|x| x[0]}.each do |aChapNum, aChapter|
        if aChapNum != 'format'
          li { makeLink(aChapter[0],aChapter[1]) }
        end
      end
    end
    
    para do <<-END_PARAGRAPH
      (<a href="http://www1.tf.chiba-u.jp/~shin/tutorial/">Japanese translation</a>
      by&nbsp;Shin&nbsp;Nishiyama.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      (<a href="http://www.ruby-doc.org/docs/ApprendreProgrammer/Apprendre_%E0_Programmer.pdf">French translation</a>
      by&nbsp;Jean&#8209;Pierre&nbsp;ANGHEL.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      (<a href="http://www.shokhirev.com/mikhail/ruby/ltp/title.html">Russian translation</a>
      by&nbsp;Mikhail&nbsp;Shokhirev.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      (<a href="http://gcarst.googlepages.com/komgodtigang">Danish translation</a>
      by&nbsp;Gunner&nbsp;Carstens.)
      END_PARAGRAPH
    end
    para do <<-END_PARAGRAPH
      (<a href="http://aprendaaprogramar.rubyonrails.pro.br/">Brazilian Portuguese translation</a>
      by&nbsp;Fabio&nbsp;Akita&nbsp;et&nbsp;al.)
      END_PARAGRAPH
    end
  end
  
  
  #
  #  MAIN PAGE GENERATION
  #
  
  def generate
    srand
    chapNum   = @cgi.params['Chapter'][0]
    chapter   = @chapters[chapNum]
    chapTitle = 'Learn to Program, by Chris Pine'
    if chapter
      chapTitle = chapNum + '.&nbsp;&nbsp;' if chapNum < 'A'
      chapTitle.sub! /^0/, ''
      chapTitle += chapter[0]
    end
    
    puts '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">'
    html(:lang=>'en') do
      head do
        link(:href=>'/stylesheets/pine.css', :rel=>'Stylesheet', :type=>'text/css', :media=>'screen')
        link(:href=>LINKADDR+'tutorial.css', :rel=>'Stylesheet', :type=>'text/css', :media=>'screen')
        title { chapTitle }
        script(:language=>'JavaScript', :src=>'http://www.gvisit.com/record.php?sid=6941c11eba5c874197e2096f9c854106', :type=>'text/javascript') {}
      end # head
      body do
      div(:id=>'pageWidth') do
        div(:id=>'headerBar') do
          div(:id=>'titlePicContainer') do
            puts '<a href="'+LINKADDR+'">'
            img(:id=>'titlePic', :width=>'418', :height=>'108', :src=>'/images/titleLTP.gif', :alt=>'Learn to Program')
            puts '</a>'
          end
          puts '<a href="'+LINKADDR+'">'
          puts '  <img id="locket" width="82" height="82" alt="just a cute picture"'
          puts '    src="/images/locketLTP.png" />'
          puts '</a>'
        end
        div(:id=>'menuPane') do
          img(:id=>'menuSpearTop', :width=>'35', :height=>'38', :src=>'/images/spearup_sm.gif')
          
          menuBookLink
          
          img(:width=>'64', :height=>'21', :style=>'padding: 30px;', :src=>'/images/swirly.gif')
          
          menuTOC
          
          img(:id=>'menuSpearBottom', :width=>'36', :height=>'40', :src=>'/images/speardown_sm.gif')
        end
        div(:id=>'contentPane') do
          if chapter
            h1 {chapTitle}
            puts @@HLINE
            method(chapter[1]).call
          else # TOC
            h2 { 'A Place to Start for the Future&nbsp;Programmer' }
            para do <<-END_PARAGRAPH
              I guess this all began back in 2002.  I was thinking
              about teaching programming, and what a great language
              Ruby would be for learning how to program.  I mean, we were
              all excited about Ruby because it was powerful, elegant, and
              really just fun, but it seemed to me that it would also
              be a great way to get into programming in the first place.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              Unfortunately, there wasn't much Ruby documentation
              geared for newbies at the time.  Some of us
              in the community were talking about what such a
              "Ruby for the Nuby" tutorial would
              need, and more generally, how to teach programming at all.
              The more I thought about this, the more I had to say (which
              surprised me a bit).  Finally, someone said, "Chris,
              why don't you just write a tutorial instead of talking about
              it?"  So I did.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              And it wasn't very good.  I had all these ideas that were good
              <em>in theory</em>, but the actual task of making a great
              tutorial for non-programmers was vastly more challenging than
              I had realized.  (I mean, it seemed good to me, but I already
              knew how to program.)
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              What saved me was that I made it really easy for people to
              contact me, and I always tried to help people when they got
              stuck.  When I saw a lot of people getting stuck in one place,
              I'd rewrite it.  It was a lot of work, but it slowly got better
              and better.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              A couple of years later, it was getting pretty good.  :-)  So
              good, in fact, that I was ready to pronounce it finished, and
              move on to something else.  And right about then came an
              opportunity to turn the tutorial into a book.  Since it was
              already basically done, I figured this would be no problem.
              I'd just clean up a few spots, add some more exercises, maybe
              some more examples, a few more chapters, run it by 50 more
              reviewers...
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              It took me another year, but now I think it's really
              <em>really</em> good, mostly because of the hundreds of
              brave souls who have helped me write it.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              What's here on this site is the original tutorial, more or less
              unchanged since 2004.  For the latest and greatest, you'll
              want to check out <a href="#{FRLTP_ADDR}">the book</a>.
              END_PARAGRAPH
            end
            puts @@HLINE
            h2 { 'Thoughts For Teachers' }
            para do <<-END_PARAGRAPH
              There were a few guiding principles that I tried to stick to.
              I think they make the learning process much smoother;
              learning to program is hard enough as it is.  If you're
              teaching or guiding someone on the road to hackerdom, these
              ideas might help you, too.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              First, I tried to separate concepts as much as possible,
              so that the student would only have to learn
              one concept at a time.  This was difficult at first, but a little
              <em>too</em> easy after I had some practice.  Some things must be
              taught before others, but I was amazed at how little of
              a precedence hierarchy there really is.  Eventually, I just had to
              pick an order, and I tried to arrange things so that each
              new section was motivated by the previous ones.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              Another principle I've kept in mind is to teach only one way
              to do something.  It's an obvious benefit in a tutorial for
              people who have never programmed before.  For one thing,
              one way to do something is easier to learn than two.  Perhaps
              the more important benefit, though, is that the fewer things
              you teach a new programmer, the more creative and clever
              they have to be in their programming.  Since so much of programming
              is problem solving, it's crucial to encourage that as much
              as possible at every stage.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              I have tried to piggy-back programming concepts onto concepts
              the new programmer already has; to present ideas in such a way
              that their intuition will carry the load, rather than the
              tutorial.  Object-Oriented programming lends itself to this
              quite well.  I was able to begin referring to "objects" and
              different "kinds of objects" pretty early in the tutorial,
              slipping those phrases in at the most innocent of moments.
              I wasn't saying anything like "everything in Ruby is an
              object," or "numbers and strings are kinds of objects,"
              because these statements really don't mean anything to
              a new programmer.  Instead, I would talk about strings
              (not "string objects"), and sometimes I would refer to
              "objects", simply meaning "the things in these programs."
              The fact that all these <em>things</em> in Ruby <em>are</em> objects
              made this sort of sneakiness on my part work so well.
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              Although I wanted to avoid needless OO jargon, I wanted
              to make sure that, if they did need to learn a word, they
              learned the right one.  (I don't want them to have to learn
              it twice, right?)  So I called them "strings," not "text."  Methods
              needed to be called something, so I called them "methods."
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              As far as the exercises are concerned, I think I came up
              with some good ones, but you can never have too many.
              Honestly, I bet I spent half of my time just trying to
              come up with fun, interesting exercises.
              Boring exercises absolutely kill any desire
              to program, while the perfect exercise creates an itch
              the new programmer can't help but scratch.  In short,
              you just can't spend too much time coming up with good
              exercises.
              END_PARAGRAPH
            end
            puts @@HLINE
            h2 { 'About the Original Tutorial' }
            para do <<-END_PARAGRAPH
              The pages of the tutorial (and even this page) are generated by a
              <a href="#{LINKADDR}?ShowTutorialCode=true">big Ruby program</a>,
              of course.  :-)
              As such, it has some neat features.  For example, all of the
              code samples are actually being run every time you view
              the page, and the output shown is the output they generate.
              I think this is the best, easiest, and
              certainly the coolest way to make sure that all of the
              code I present works <em>exactly</em> as I say it does.
              You don't have to worry that I might have copied the output
              of one of the examples
              wrong, or forgotten to test some of the code; it's all tested
              every time you see it.  So in the section on random number
              generators, if you reload the page you will see the numbers
              change each time... <em>nice</em>.
              (I used a similar trick for the example code when writing
              the book, but it's obviously more apparent with the tutorial.)
              END_PARAGRAPH
            end
            para do
              '<a href="http://ruby-lang.org">'+
                '<img src="/images/PoweredByRuby.png" alt="powered by Ruby" width="234" height="60" />'+
              '</a>'
            end
            puts @@HLINE
            h2 { 'Acknowledgements' }
            para do <<-END_PARAGRAPH
              Finally, I'd like to thank everyone on the ruby-talk mailing list
              for their thoughts and encouragement, all of my wonderful
              reviewers for their help in making the book far better than
              I could have alone, my dear wife especially
              for being my main reviewer/tester/guinea pig/muse,
              Matz for creating this fabulous language, and the Pragmatic Programmers
              for telling me about it&mdash;and, of course, for publishing
              my book!
              END_PARAGRAPH
            end
            para do <<-END_PARAGRAPH
              If you notice any errors or typos, or have any comments or
              suggestions or good exercises I could include, please
              <a href="mailto:chris@pine.fm">let me know</a>.
              END_PARAGRAPH
            end
          end
          
          puts @@HLINE
          para(:style=>'padding-bottom: 20px;') { "&copy; 2003-#{Time.now.year} Chris Pine" }
        end # contentPane
      end # pageWidth
      end # body
    end # html
  end
  
  def self.handle_request cgi
    begin
      if cgi.params['ShowTutorialCode'][0]
        tutorialSource = File.read __FILE__
        cgi.out('text/plain') { tutorialSource }
      else
        page = self.new cgi
        page.generate
        page.out
      end
    rescue Exception => e
      error_msg = <<-END_ERROR
        <html><head><title>ERROR</title></head>
        <body><h3>ERROR:  email Chris or Katy with this page's address</h3>
        <pre><strong>#{e.class}:  #{CGI::escapeHTML(e.message)}</strong>
        #{e.backtrace.join("\n")}
        </pre>
        </body></html>
      END_ERROR
      cgi.out { error_msg }
    end
  end
end
