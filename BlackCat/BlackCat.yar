/*
BlackCat / ALPHV ransomware
*/

rule BlackCat
{
    meta:
        author = "Andrey Zhdanov"
        company = "Group-IB"
        family = "ransomware.blackcat"
        description = "BlackCat ransomware Windows/Linux payload"
        severity = 10
        score = 100

    strings:
        $n0 = { ( B8 01 00 00 00 31 C9 | 31 C9 B8 01 00 00 00 )
                [0-2] 89 DE 0F A2 87 F3 89 CE [0-8]
                ( B8 07 00 00 00 31 C9 | 31 C9 B8 07 00 00 00 )
                [0-2] 81 E6 00 00 00 02 [0-2] 0F A2 [0-14] C1 E8 19 85 F6 }
        $n1 = { ( B8 01 00 00 00 31 C9 | 31 C9 B8 01 00 00 00 )
                ( 89 | 48 89 ) DE 0F A2 ( 87 | 48 87 ) F3 89 C?
                ( B8 07 00 00 00 31 C9 | 31 C9 B8 07 00 00 00 )
                [0-4] 0F A2 [0-8] C1 E? 19 ( 24 01 | 40 80 E6 01 ) }
        $c0 = { 66 0F 72 ( F? 0C 66 0F 72 D? 14 | D? 14 66 0F 72 F? 0C )
                66 0F EB ?? }
        $c1 = { 66 0F 72 ( F? 07 66 0F 72 D? 19 | D? 19 66 0F 72 F? 07 )
                66 0F EB ?? }

        $x0 = { 8D ( 4D ?? | 4C 24 ?? | 8D ?? FF FF FF) BA [4]
                68 1A 0C 06 00 E8 }
        $x1 = { 8D ( 4D | 4C 24 ) ?? BA [4] 6A 7B E8 }
        $y0 = { 68 1A 0C 06 00 68 [4] 50 E8 }
        $y1 = { 6A 7B 68 [4] 50 E8 }
        $z0  = { 68 C0 1F 00 00 68 [4] 5? E8 }

        $a01 = "src/bin/encrypt_app/app.rs" ascii
        $a02 = "encrypt_app::windows" ascii
        $a03 = "src/bin/encrypt_app/windows.rs" ascii
        $a04 = "encrypt_app::linux" ascii
        $a05 = "src/bin/encrypt_app/linux.rs" ascii
        $a06 = "library/encrypt-lib/src/app.rs" ascii
        $a07 = "encrypt_lib::windows" ascii
        $a08 = "library/encrypt-lib/src/windows.rs" ascii
        $a09 = "library/encrypt-lib/src/linux.rs" ascii
        $a10 = "encrypt_lib::linux" ascii
        $a11 = "psexec_args=" ascii
        $a12 = "psexec_args::args=" ascii
        $a13 = "locker::core::" ascii
        $a14 = "set_desktop_image::" ascii
        $a15 = "::pipeline::file_worker_pool" ascii
        $a16 = "::pipeline::chunk_workers_supervisor" ascii
        $a17 = "::os::windows::privilege_escalation" ascii
        $a18 = "::os::windows::samba" ascii
        $a19 = "::os::windows::system_info" ascii
        $a20 = "::os::windows::netbios" ascii
        $a21 = "hidden_partitions::mount_all::mounting=" ascii
        $a22 = "uac_bypass::shell_exec=" ascii
        $a23 = "-u-p-s-d-f-cpropagate::attempt=" ascii
        $a24 = "enum_dependent_services" ascii
        $a25 = "masquerade_peb" ascii
        $a26 = "AdvancedSmartPattern" ascii

        $b01 = "note_file_name" ascii
        $b02 = "note_full_text" ascii
        $b03 = "note_short_text" ascii
        $b04 = "default_file_cipher" ascii
        $b05 = "default_file_mode" ascii
        $b06 = "note_full_text" ascii
        $b07 = "exclude_file_path_wildcard" ascii
        $b08 = "exclude_file_extensions" ascii
        $b09 = "enable_network_discovery" ascii
        $b10 = "enable_self_propagation" ascii
        $b11 = "enable_set_wallpaper" ascii
        $b12 = "enable_esxi_vm_kill" ascii
        $b13 = "enable_esxi_vm_snapshot_kill" ascii
        $b14 = "strict_include_paths" ascii
        $b15 = "esxi_vm_kill_exclude" ascii
        $b16 = "drop-drag-and-drop-target" ascii
        $b17 = "no-vm-kill" ascii
        $b18 = "no-vm-snapshot-kill" ascii
        $b19 = "no-prop-servers" ascii

    condition:
        (((uint16(0) == 0x5A4D) and (uint32(uint32(0x3C)) == 0x00004550)) or
         (uint32(0) == 0x464C457F)) and
        (
            ((1 of ($n*)) and (2 of ($c*))) or
            ($z0 and ((all of ($x*)) or (all of ($y*)))) or
            (7 of ($a*)) or
            (5 of ($b*))
        )
}
