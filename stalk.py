import frida
import argparse


STALKER_JS = """
Process.enumerateModules({
    onMatch: function(module){
        console.log('Module name: ' + module.name + " - " + "Base Address: " + module.base.toString());
    },
    onComplete: function(){}
});


/*const mod_java = Process.findModuleByName("libjvm.dylib");
mod_java.enumerateSymbols().forEach( function(s) {
    console.log(s.name)
})*/

Interceptor.attach(Module.getExportByName('libjvm.dylib', "JVM_ArrayCopy"), {
    onEnter: function(args) {

    },
    onLeave: function (retval) {
        //Process.getCurrentThreadId()

        console.log(
            Thread.backtrace(
                this.context,
                Backtracer.ACCURATE
            )//.map(DebugSymbol.fromAddress)
        );
    }
});


const threads = Process.enumerateThreads();
threads.forEach(function(t) {
  console.log(t.id + " : " + t.state + " : " + DebugSymbol.fromAddress(t.context.pc) );

  /*console.log(
    Thread.backtrace(
        t.context,
        Backtracer.ACCURATE
    ).map(DebugSymbol.fromAddress)
  )*/
});

if( Java.available ) {
    console.log("FOUND JAVA");
}

if( ObjC.available ) {
    console.log("FOUND OBJC");
}


threads.forEach(function(t) {
    Stalker.follow(t.id, {
        events: {
        call: true,
        ret: false,
        exec: false,
        block: false,
        compile: false
        },
        //onReceive: function (events) {
        //    console.log(t.id + " : " + Stalker.parse(events));
        //},
        onCallSummary: function (summary) {
            //console.log( summary );
            console.log(t.id + " " + summary)
            /*Object.keys(summary).forEach(function (target) {
                var count = summary[target];
                console.log(target + " : " + count)
                //targets[target] = (targets[target] || 0) + count;
            });*/
        },
    })
});

/*Stalker.follow(mainThread.id, {
    events: {
        call: true,
        ret: false,
        exec: false,
        block: false,
        compile: false
    },
    onReceive: function (events) {
        console.log(Stalker.parse(events));
    }
    onCallSummary: function (summary) {
        console.log( summary );
    },
});*/
"""

STALKER_JS_DOWN = """
const threads = Process.enumerateThreads();

threads.forEach(function(t) {
    Stalker.unfollow(t.id);
});

"""

def on_message(message, data):
	print("[%s] -> %s" % (message, data) )

def main():
    parser = argparse.ArgumentParser(description='fuzz and trace stuff.')
    parser.add_argument('-p', '--process', type=int, help='process id')
    #parser.add_argument('-c', '--spawn', help='process id')

    args = parser.parse_args()

    session = frida.attach( args.process )
    #session = frida.spawn( args.spawn )
    #spawn = ["/usr/bin/java", "-cp", "/", "Foo"]
    #pid = frida.spawn( spawn)
    #session = frida.attach( pid )
    script = session.create_script( STALKER_JS )

    script.on('message', on_message)
    script.load()

    input('[!] Press <Enter> at any time to detach from instrumented program.\n\n')

    #session.create_script( STALKER_JS_DOWN ).load()

    session.detach()


if __name__== "__main__":
    main()
