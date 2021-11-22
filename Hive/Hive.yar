/*
Hive ransomware
*/


rule Hive_v3
{
    meta:
        author = "rivitna"
        company = "Group-IB"
        family = "ransomware.hive"
        description = "Hive v3 ransomware Windows/Unix payload"
        severity = 10
        score = 100

    strings:
        $h0 = { B? 03 52 DA 8D [6-12] 69 ?? 00 70 0E 00 [14-20]
                8D ?? 00 90 01 00 }
        $h1 = { B? 37 48 60 80 [4-12] 69 ?? 00 F4 0F 00 [2-10]
                8D ?? 00 0C 00 00 }
        $h2 = { B? 3E 0A D7 A3 [2-6] C1 E? ( 0F | 2F 4?)
                69 ?? 00 90 01 00 }

    condition:
        (((uint16(0) == 0x5A4D) and (uint32(uint32(0x3C)) == 0x00004550)) or
         (uint32(0) == 0x464C457F)) and
        (
            (2 of ($h*))
        )
}
