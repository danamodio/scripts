import frida
import sys


def on_detached():
    print("on_detached")

def on_detached_with_reason(reason):
    print("on_detached_with_reason:", reason)

def on_detached_with_varargs(*args):
    print("on_detached_with_varargs:", args)

#print frida.get_device_manager().enumerate_devices()

#process = frida.get_device_manager().enumerate_devices()[2].spawn("com.....")

usb = frida.get_usb_device()
pid = usb.spawn(["com.boardbooks.boardbooks"])
#print dir(pid)
sess = usb.attach( pid )
#print dir(sess)
sess.on('detached', on_detached)
sess.on('detached', on_detached_with_reason)
sess.on('detached', on_detached_with_varargs)

print "[*] Enumerated Modules:"
for m in sess.enumerate_modules():
    print "    " + m.path

print "\n[*] Instrumenting..."

def on_message(message, data):
    if "payload" in message:
        print message["payload"]
    else:
        print message;

jscode = """
//send("hello world")
'use strict';

//var masked_files = ["/var", "/private", "/private/var", "/System"];
var masked_files = [];

// NOISY!!!
Interceptor.attach(Module.findExportByName(null, 'objc_msgSend'), {
  onEnter: function (args, context) {
    // todo -- batch..
    //send('objc_msgSend() ' + context.r0.toInt23());
    //send(Object.keys(args).join(","))
    var className = ObjC.Object(args[0]).$className
    var sel = ObjC.selectorAsString(args[1])
    send("["+className+" "+sel+"]")
    //send(className)
    //send(ObjC.Object(args[2]).toString())
  }
});

Interceptor.attach(Module.findExportByName(null, 'open'), {
  onEnter: function (args) {
    this.path = Memory.readUtf8String(args[0]);
    //send('open("' +this. path + '")');
  },
  onLeave: function (retval) {
    if(masked_files.indexOf( this.path ) > -1) {
        //send('[!] Overriding return value for open('+this.path+') to -1');
        retval.replace(0xFFFFFFFF);
        send('[!] open('+this.path+') : '+retval.toInt32());
    } else {
        send('open('+this.path+') : '+retval.toInt32());
    }
  }

});

Interceptor.attach(Module.findExportByName(null, 'opendir'), {
  onEnter: function (args) {
    var path = Memory.readUtf8String(args[0]);
    send('opendir("' + path + '")');
  }
});

Interceptor.attach(Module.findExportByName(null, 'dlopen'), {
  onEnter: function (args) {
    var path = Memory.readUtf8String(args[0]);
    send('dlopen("' + path + '")');
  }
});

Interceptor.attach(Module.findExportByName(null, 'access'), {
  onEnter: function (args) {
    var path = Memory.readUtf8String(args[0]);
    send('access("' + path + '")');
  }
});

//Interceptor.attach(Module.findExportByName(null, 'snprintf_l'), {
//  onEnter: function (args) {
      // its actually a pointer i thinkg.. this will just get mem address
//    var str = Memory.readUtf8String(args[0]);
//    send('snprintf_l("' + str + '")');
//  }
//});

Interceptor.attach(Module.findExportByName(null, 'fopen'), {
  onEnter: function (args) {
    this.path = Memory.readUtf8String(args[0]);
    //send('fopen("' + this.path + '")');
  },
  onLeave: function (retval) {
    if(masked_files.indexOf( this.path ) > -1) {
        //send('[!] Overriding return value for fopen('+this.path+') to -1');
        retval.replace(0xFFFFFFFF);
        send('[!] fopen('+this.path+') : '+retval.toInt32());
    } else {
        send('fopen('+this.path+') : '+retval.toInt32());
    }

  }
});

Interceptor.attach(Module.findExportByName(null, 'system'), {
  onEnter: function (args) {
    var cmd = Memory.readUtf8String(args[0]);
    send('system("' + cmd + '")');
  }
});

Interceptor.attach(Module.findExportByName(null, 'stat'), {
  onEnter: function (args) {
    var path = Memory.readUtf8String(args[0]);
    send('stat("' + path + '")');
    // this should work...
    //send('stat()');
  }
});

Interceptor.attach(Module.findExportByName(null, 'fstat'), {
  onEnter: function (args) {
    //var path = Memory.readUtf8String(args[0]);
    var fd = args[0].toInt32();
    //send('fstat("' + path + '")');
    send('fstat('+fd+')');
  }
});

Interceptor.attach(Module.findExportByName(null, 'lstat'), {
  onEnter: function (args) {
    this.path = Memory.readUtf8String(args[0]);
    this.buff = args[1];
    //send('lstat("' + this.path + '")');
  },
  onLeave: function (retval) {
    if(masked_files.indexOf( this.path ) > -1) {
        //send('[!] Overriding return value for lstat('+this.path+') to -1');
        send('[!] lstat("' + this.path + '")');
        retval.replace(0xFFFFFFFF);
    } else {
        send('lstat("' + this.path + '")');
    }
    //send( retval.toInt32() );
  }
});


// OBJECTIVE X
if(ObjC.available) {

for(var className in ObjC.classes) {
  if (ObjC.classes.hasOwnProperty(className)) {

    if(className == "NSFileManager") {
        send("Found target class : " + className);

        Interceptor.attach( ObjC.classes.NSFileManager["- fileSystemRepresentationWithPath:"]   , {
          onEnter: function (args) {
            var obj = ObjC.Object(args[2]);
            send('-[NSFileManager fileSystemRepresentationWithPath]: '+ obj);
          }
        });

        Interceptor.attach( ObjC.classes.NSFileManager["- stringWithFileSystemRepresentation:"]   , {
          onEnter: function (args) {
            var obj = ObjC.Object(args[2]);
            send('-[NSFileManager stringWithFileSystemRepresentation]: '+ obj);
          }
        });

    }

    // -[NSPlaceholderString initWithCString
    // initWithCharactersNoCopy
    // initWithBytes
    //

    // +[NSMutableString initialize]

    if(className == "NSString") {
        send("Found target class : " + className);

        // writeToFile

        Interceptor.attach( ObjC.classes.NSString["- init:"]   , {
          onEnter: function (args) {
            //var obj = ObjC.Object(args[0]);
            //send('NSString("' + obj.toString() + '")');
            // ObjC.selectorAsString(args[1])
            // var receiver = new ObjC.Object(args[0]);
            // var sel = ObjC.selectorAsString(args[1]);
            var obj = ObjC.Object(args[2]);
            send('-[NSString init]: '+ obj);
          }
        });

    }

  }
}


} else {
    send("Objective-C Runtime is not available!");
    //console.log("Objective-C Runtime is not available!");
}

"""

script = sess.create_script(jscode)
script.on('message', on_message)
script.load()

usb.resume( pid )

sys.stdin.read()
