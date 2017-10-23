# Repo for VOS Related Scripts

For any questions please contact:

John Vasconcelos

john.vasconcelos@harmonicinc.com

or

Satish Botla

satish.botla@harmonicinc.com

---

# Script: vos_migrate_services.py
# Dependency:vos.py

**Ruunning the Script Example** 
```
./vos_migrate_services.py --rt_from vosdashboard.dfwcpcorange.ds.dtvops.net --rt_to vosdashboard.dfwcpcpurple.pod2.ds.dtvops.net --serv_file or_srv.txt --src_file or_src.txt --ats_file or_ats.txt  --blackout_img http://dfwlive-sponsored.akamaized.net/TV-tvOS-Messaging-fullscreen-blackout-no-rights.jpg --sigloss_img http://dfwlive-sponsored.akamaized.net/TV-tvOS-Messaging-fullscreen-input-loss.png --enable_drm --single_prof --sp_file sp.txt
```

**Script Arguments**
**--rt_from** --> The cluster from which to migrate the configuration from:

**--rt_to** --> The cluster to which the configuration will be migrated.

**--blackout_img** --> The Blackout image URL to be used on Service Add-on.

**--sigloss_img** --> The Signal Loss image to be used on Source configuration.

**--enable_drm** --> Indicates that the DRM systems/settings configuration need to be copied to the new cluster. (Required on systems with DRM)

**--serv_file** --> List of services to be migrated from one cluster to another. 
Format:
```
AandEHD-1382.dfw.1080.tv
FNCHD-1380.dfw.720.tv
AMCHD-4730.dfw.1080.tv
```

**--src_file** --> List of Sources to new CL Assignment to be migrated to new cluster.
Format:
```
AandE.AandEHD-1382.1080.eng.p,MSSN46p
AMC.AMCHD-4730.1080.eng.p,MSSN46p
FoxNewsChannel.FNCHD-1380.720.eng.p,MSSN47p
FoxNewsChannel.FNCHD-1380.720.eng.b,MSSN47b
```

**--ats_file** --> List of ATS Destinations to be Migrated to the new cluster. Multicast information, new CL assignment and destination profile ID are required to be in this file.
Format:
```
FNCHD-1380.dfw.720.tv.ATS,239.243.248.63,40000,EMSSN48p,4a615c16-b23f-bcbd-9f0c-25fb77bc9914
```
**--single_prof** --> Use this option to convert tv/mobile services to Single Profile.

**--sp_file** --> List of Profiles to use for each of the single profiles to be used with their corresponding IDs

Format:
```
dfw.720,b9fb7c25-dd8f-868f-96be-1f02115c3fd6
dfw.480,29288a15-c5b6-695d-f38a-0113c6226b7d
dfw.1080,79ee6444-7521-b66f-ad17-7fa7e9a09a12
dfw.origin,99686edd-ac8a-a87f-0524-fd5af40c1a85
gmott.origin,2d8ff877-a7e5-7096-a872-eefd5780068f
```