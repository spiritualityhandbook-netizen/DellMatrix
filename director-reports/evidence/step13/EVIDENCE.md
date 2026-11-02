# EVIDENCE — Step 13: full pairwise re-derivation (9,900 pairs)

Scope: Director-order step 13 — full 9,900 ordered-pair
re-derivation at the repaired freeze, ledger v2.
Tested revision: the repaired code head the sweep ran against
(step 11 merge lineage; see STEP13_PACKET.md for the exact
anchor and the final counts: FUNCTIONAL 1,989 /
FUNCTIONAL_INDEPENDENT 6,375 / INTENDED_CLASH 1,528 /
UNIQUE 8; DEFECT 0; identity 89 IDEMPOTENT / 11 HONEST_REFUSAL).
Commands: gate0_census.py (baseline census), gate1_pilot.py
(pilot), gate2_sweep.py (full sweep in 100 blocks under sweep/),
then the merge into step13_rederived.json and diff_vs_v1.json
against gate4_ledger_v1.json.
Environment limits: local Linux VM, Python 3.12; the sweep is a
harness run against per-owner isolated Program state, not a
public-entry-path execution; classification semantics are the
frozen Gate-0 seed's (see the packet).
Gaps: none known for the listed artifacts; earlier Gate-era
logs superseded by this re-derivation are history, not evidence
for step 13, and are not included.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| STEP13_PACKET.md | 72828c91cae43e600e26d59da3c0893f202c5578aac8559b45c5413edcaa6743 | 11423 |
| census_run.log | c842802bba38ac8fa0f55e43f62f44b465abd2b99a9583932f106e1b36a7cf39 | 6405 |
| diff_vs_v1.json | a7de1faef1b11e18847aace4ea7b704e68ac5b89cfe0cd08fe22a28da153f09e | 52624 |
| gate0_census.py | 3395573cbec21ee83b0593260314782906508d0f1460d110e8ddf7fcfe862d69 | 9169 |
| gate0_census_main.json | c22888180be21cd2a5c3a2e5e6e48b2f2c6c3cf2cd1ac439adcff0ab1bf9f677 | 21664 |
| gate1_pilot.py | ac2f3ce30870ef361f676b13a4358aabd7596c5583f9a0d8abdf0539efd8c833 | 8758 |
| gate2_sweep.py | f1910d63d959106fe7277a7b8a6c6ea28978a94b540dd72498359576c6e12610 | 7396 |
| gate4_ledger_v1.json | d419220707b26da7c4a35cb34ff0a55cdc320cb64852026a7d9cc36503b39c3c | 4755847 |
| gate4_ledger_v2.json | 061472c9232bd29be3c6ab8ca25136288dd4507ec9f5f5cc7411408e34388c90 | 4777994 |
| step13_ground.md | c74a48002e5af01e1f741fe7e8512a0730c936737f0fdae6eb038bc37eecf533 | 15304 |
| step13_rederive.py | cc14ba642cd924090faa45aa2d83b6a9656bd54c9afe0f3de70d7309cc61cef3 | 7306 |
| step13_rederived.json | e1a3bb8f64786d29e3ff8c4faad1d543e43a2266ac3a763f82b4e2c0c2869823 | 4871960 |
| sweep/block_00.json | 21d66279a5201adcda1de56d1813fe30fcbfe94ca290ec64a4a0bc3bd2365210 | 32651 |
| sweep/block_01.json | 506c8dd42abe82c89f3d3aeefff57f1ee52346787c3b39aa461cc81d8efc9197 | 36292 |
| sweep/block_02.json | b7a9d2c922b9e6bd7f7e5734a053f289c21e9175ca7ecd2da78651a9ae9a1394 | 36232 |
| sweep/block_03.json | 2f4d2659731c5678d42fa344fe8239add66b05ec51ea842cb1010c360d3c88f7 | 36333 |
| sweep/block_04.json | c970c1b28319a673a88fd1d646c17946556aa6b42408b1e629b0cb0abd5fa2f5 | 36088 |
| sweep/block_05.json | 48e8c865398ac55858a68ca0706b4020ac934baeaba7e06447ecb5f79183d568 | 40574 |
| sweep/block_06.json | 8683f4021ee120f5525e61688bc05504cbf19066b574a6c695b967cf4f35ee29 | 45627 |
| sweep/block_07.json | 0b257842f7a790e644e4a34601a161101d63813355bfcee2021813d5695617b1 | 41826 |
| sweep/block_08.json | ee34da3807933ec99c2e5901fada76402f0086be22547ed06813446d8719c6c8 | 42846 |
| sweep/block_09.json | f1af4dd541e2e765032efe61a3be99184f2619dcb1dca1e46f294e5791450b2e | 40995 |
| sweep/block_10.json | 60e63b59628f0bfbbbf356db161ab8a1eb5166d1eaa831721323124f5c3e1d1d | 35863 |
| sweep/block_11.json | 62b6f267079b29e44421caf6b8f969ba4b6f66e9f5e9a6ec6c7cc43b6ee2f608 | 32287 |
| sweep/block_12.json | 587ab5dcdfdccc007d639bc6f45dd5f0b229e5b50d0b36b57f7e82830d025678 | 35852 |
| sweep/block_13.json | e3238abed6fa7ef89b7dc18972dc8d390ed83d647b377ecaa2998810767d0d08 | 35915 |
| sweep/block_14.json | 0641aae811dcfa2ce8fda971511a0edeba0e9c57e9ee77efd503952748dba04a | 35701 |
| sweep/block_15.json | cc66e0b20b40899623f7c7c5550cb948db6973835a38cef2b493da8b024b7106 | 39921 |
| sweep/block_16.json | df47c88219156b422205782f2253c650904da0d8cc759625fbccf46ee0d287c8 | 44726 |
| sweep/block_17.json | a6bfcd323aa7a158201b72753f6e6257fd7bf01bcbe0ff4836d05c200fde3872 | 41137 |
| sweep/block_18.json | 8717b202d1093368fc980055fb95e64c67e356e803b9ca18202d8d3c07e2278e | 42217 |
| sweep/block_19.json | 8ac5f6368f0085b49d786afb24c5dbd9190abb2657ddb70ef15d6bea8ff75ee7 | 40393 |
| sweep/block_20.json | 53f7f92b9eeb5efc0b87728c1126fd6d93a3ac222cf8c1381751b9fcdedc9084 | 36279 |
| sweep/block_21.json | d040b0b8e17b9ee330cc30268aabb380d36ccef6057b14d2017b68360427359f | 36211 |
| sweep/block_22.json | 2669e0dc2723501f315ba86e99247c6509f3e0ad4a8e00ecba558f4121163708 | 32635 |
| sweep/block_23.json | 3e279e1e68ace5fb19d955104d4f3c6ed6917f94b09548ab4238dc755f4e77d6 | 36325 |
| sweep/block_24.json | d60eb010eecb679bac4ed009daa1abb15468558648c5a14a4a862e8973330364 | 36114 |
| sweep/block_25.json | a8e91ebaa39d3c94ce56fbab4e106b30358767c62cbb17c9c63429229db1ac96 | 40209 |
| sweep/block_26.json | ff94b27dda0ce1a3a5bcd41573564ddb010dc64552f973620772812dc7278994 | 44656 |
| sweep/block_27.json | 325cd4c9bafea758b42c64ae576dfe4c57bc3573a59eed26d661be7f3a92c90e | 41280 |
| sweep/block_28.json | 46f875684323be84fb200e0c52de5cfd68052b12da532a3fdf2df45249344e63 | 42270 |
| sweep/block_29.json | 5b9b01df277bc4143244b4e69d62249728b767c491c5d5202b9ab086c79ef12f | 40564 |
| sweep/block_30.json | a34656de74d3c895282fc383de692558169c26120438e58ff3ae0d7a04ad85a9 | 36265 |
| sweep/block_31.json | 444d159855cf98e8ac2c485fe64bc8edc90fc3cad17037a21a7e2bc1e435b383 | 36281 |
| sweep/block_32.json | 3973e499fd010d332c4d88239707d44481bb0645fc18ff4b58e47614aac6ef49 | 36227 |
| sweep/block_33.json | eb0ac33248a39b4c8bea4c2a69f40f2b5a705c6e89b64bbb50fc42513b8c7fcd | 32699 |
| sweep/block_34.json | d15c2d4344e0d29e52adff85ccbbfe20318cf685d2a210df4ef88f9829cd2dda | 36076 |
| sweep/block_35.json | 618fc5dde15c8e46a4fcd822178d96814fa9e19a04cb01edf4a701dbbe2d29a5 | 40561 |
| sweep/block_36.json | 0644b5cdddba457429769e40068b50a9eaddb96b2159d304666674f0debe94d0 | 45617 |
| sweep/block_37.json | eed6d1af28867a1439844e682723c50be43dbb904cc75a92bb606203f67781be | 41818 |
| sweep/block_38.json | ab24d554e504134d136e2a0019dbfbf41257e4418f2d842aa6aa14ee714fd7d4 | 42837 |
| sweep/block_39.json | 6c7ebabec7aa8e4fa16e079d072501ba1a6c306cb33de96d20b0c7c2c0432db9 | 40987 |
| sweep/block_40.json | aedf1468ff1a404521f19e37e7b64a716c30e4357572d2d9c8291e09ff5f98ed | 36220 |
| sweep/block_41.json | fb14c5b06b212f5f5f30b679088cc5e104a80ea0600f8cb8fe1a2f8543200e8e | 36201 |
| sweep/block_42.json | 4a79a2c6802a872a2aea089bb62fe0ed40768b29084242a54b556e94bef91498 | 36197 |
| sweep/block_43.json | d4160552ca124ead739ddd4e880a110f8b46e8e48b78796e56b66346c4a838e0 | 36267 |
| sweep/block_44.json | 7c2a9c957ee7bf7f99514491c591960d8d7ac39f878d5ce8540ac39c80d477b7 | 32425 |
| sweep/block_45.json | 0c7f276cf621723d7d2a28fde538a7faf2b14bb5b38c70cddc8202ae5e6e99cd | 40075 |
| sweep/block_46.json | 07549f39beed03affff50b837733aa39d1415f3a43ce71795c6f20619b995c26 | 44596 |
| sweep/block_47.json | 44ae6097659b6f907d7485b8981dd59d4dd876a272ef2f0d0bf7350a6e036826 | 41220 |
| sweep/block_48.json | d6a5863940417a39d9d1711b7df0ad769cd88dd51753f494e1c0249fc8f06669 | 42211 |
| sweep/block_49.json | 6359e1508b52542802a86ffd97d14ddb2c920ce4f83400b9dc171f6e483b28b6 | 40508 |
| sweep/block_50.json | 8fb8d457927cd49e388ba683d35716c241991ebeb816e8e8e391f10875443817 | 38416 |
| sweep/block_51.json | e2f1293ea4617da5ad3457151e1afc406ac66e04f8bf9fc373679a318e6e366c | 38476 |
| sweep/block_52.json | e223e501c4c216417c8d584b55c470484e9f7a1c268539de6092224ab084d1a5 | 38373 |
| sweep/block_53.json | 47523513408efc2bdbd4ccf88c3ca36655e2e7f29766c86cd7330ea6a9b064ca | 38472 |
| sweep/block_54.json | 538d4f7d7bd0ca261d03ca554fce1ed5ed51c7607e0a9149e7f65d0d2ba4d19c | 38193 |
| sweep/block_55.json | 256f767060b5ce358aa00772a19d963f96e710b82646d3915de9267b39e16efa | 38415 |
| sweep/block_56.json | 257b01e4c4e5d002ae6ec321e5331e60865d4e4993a7be07918297d4a43c840d | 47768 |
| sweep/block_57.json | 427947023e3a10dbdc31a85e207885e359fa06dfc99d9e1d9c6e3e3f79cf29bc | 43967 |
| sweep/block_58.json | 93fdd1aed0088090892c197589ef5a066a5c2f4d34dd40e27c706c177ea0e79d | 44991 |
| sweep/block_59.json | 12b3d6b8dcf011450fcc7ec6e6d8b0ca020bd62ab01bbefd1d43c6bce96e6fc3 | 43064 |
| sweep/block_60.json | 89f314a26790e6c376c17095b58de3f8d1ad887ec656900ec2cb604b466e05f5 | 40746 |
| sweep/block_61.json | 171a374198ea33e377ee9f0feb60a38e2f45a676549ccba4e1f23ffaf5e61c80 | 40805 |
| sweep/block_62.json | ee7c511315852d6ab56aa71e6a733ffcb32268ee37cab9d35d40576f6719358f | 40705 |
| sweep/block_63.json | 6f1baa893365ecf173835d71fb50cc03c2f539956c62773ad7245f3998e83aaf | 40805 |
| sweep/block_64.json | 33004c3b7935f85e1ef9ba05de0bee69e482f09646f1c23ac081ded172609e08 | 40882 |
| sweep/block_65.json | 52212909cb92a8cfc2dab352fd0bf1957030c54873e2b43edac79cef520a484f | 45008 |
| sweep/block_66.json | f0e51fffd0de06ddb34f3931432a4908863af3d6530098180a0527ea7cd4b8d5 | 45093 |
| sweep/block_67.json | db4af3edb422114e71cc504775bfdda3826ba078a75cbf8c8f8412431cc43098 | 46298 |
| sweep/block_68.json | 6f76cb6b4d86e0656f0888cd5644795e6ee4e3b3f414c784c022201f701addaa | 47317 |
| sweep/block_69.json | dd4610cd3f8b9b3bcc7519ee0cc999156841f4d544902d56efc67326699c293f | 45468 |
| sweep/block_70.json | fa7e4e3ab9d624f3f57eb5a2f951ca32bb3ea30458cb24e412eb6e4d4e7e54f4 | 39065 |
| sweep/block_71.json | ad30f0956de9c54e0ffd006510628f53a726108bc3ef7ddcfe77f73a4ef38c9d | 39125 |
| sweep/block_72.json | 0797f7b96309094a772d3307379edcbc18cbe0f8f765016f3af85a2f24a0a8d4 | 39027 |
| sweep/block_73.json | 87eb62abf8ac773150f484ce7760b63941fef5dbf0795655865ee9738c56d8a9 | 39127 |
| sweep/block_74.json | cca8594c2dcdf23f3e9f484e21f5e8b7e1ce096f6e5b01eda3e862fcd4d856d4 | 38916 |
| sweep/block_75.json | 63cacdd57f13bac8eaa497caabd2618b76a1429041e70be867a247a9904f47c3 | 43328 |
| sweep/block_76.json | 99d1726ddc868bcbc9f58e271ea0b6dd81b65bbced7998c3d0a8bb6f3e6ac609 | 48418 |
| sweep/block_77.json | a8a2fe6cb78263fc5459f34bad193e4b369cb734f8ab1ecdc170033ff6fe9b9f | 40123 |
| sweep/block_78.json | 5349d7d7affe3c03d02d4b8afe018d89fb346464ca1f3cd83c10e6ba91dfa5bf | 45638 |
| sweep/block_79.json | a726044dd51e3f3e09cf5f7fda998120ec087d27974c4806a4e3cb41f8d3ba8b | 43810 |
| sweep/block_80.json | 11104bdbe7487324467deb0589c5a916a9d20319bda8e52d2e4d6f1e761249c8 | 39162 |
| sweep/block_81.json | 2f324179621d4e7f248deea6c300b10ad110b4a4c46ff917ce5c457ea51c65f5 | 39225 |
| sweep/block_82.json | 4ab163eea08414862a57ca6bd65206641695c9a1b603f38d4f3cd6af47575929 | 39138 |
| sweep/block_83.json | 35ab763ab2f0a7747998aea6c5c8e175264f2050bd4b5f940abb0f2796c15875 | 39216 |
| sweep/block_84.json | 80aaac59b0f7d864f22619aec4cb184de96f513953ca41a37d6ec0fc2c5d2c87 | 39244 |
| sweep/block_85.json | f60dc8be2c0e3846dbb323a6579359b31f835b0d9d96cacc283d85306a985722 | 43233 |
| sweep/block_86.json | 2dac3b2ee68f06baf6bd9c17e99e09c2c4d8bca8979677232e6c25c889fe4d60 | 48023 |
| sweep/block_87.json | 72872e0c48c31d0f8cb9a853cd32be6eeb665de74310071d52cde06e0b07b46f | 44438 |
| sweep/block_88.json | c4c6a491afa1171a80fb74d8e857053f5da78e3a83d458291a4977d3735ed78a | 40779 |
| sweep/block_89.json | 03fbd766ac40a62cdb2a01c5c60ca905e3548665cc931036b9bfe757526d3b82 | 43445 |
| sweep/block_90.json | a16f36b567bb872afcd04aa15d40e376f8e7946a65890f1533f3db572763b3b9 | 38701 |
| sweep/block_91.json | 30504b65670b1706a22650eaf2b4f80a124e10302246640c8449b5c878573677 | 38685 |
| sweep/block_92.json | 5caf39274abd6b7b7d5e2c9fd34e71fdeb833ecd9f362af89171297d111d28d6 | 38685 |
| sweep/block_93.json | 77a26c08c1be8368650dbec95d11954d50bad98b63bcbbc3c52fd2005bc01cf6 | 38748 |
| sweep/block_94.json | 78c37c9ec38fb48684915fd69e78b8f5ec862a0556fee3bdb2bb12f8345768a8 | 38666 |
| sweep/block_95.json | 1611bcf63debe340ab6c16446f5693adaf1ca2aac84d0225dccaba360dac7cc5 | 42544 |
| sweep/block_96.json | 78760a3e7e00cdec34bc25080ffc2a7740dedf011e17e704ec186d01d207ae32 | 47076 |
| sweep/block_97.json | 8363b4cac33064896507bc4ff42357f197d8435c47abc3f572ad9c3252f4e9e6 | 43618 |
| sweep/block_98.json | e930cd9cc74a2d1264752e0c6a9f48d303280894587d376a4965e0c9e611b2be | 44773 |
| sweep/block_99.json | 70ab9f03ade164d8430c795dcaae900efea76182909d47fe96a878d66a1a89c1 | 38674 |
| sweep/identity.json | 91f2dc17a8f7d17e37f702b176abf9508d52831a7b1816f4d59342c3e496bb2c | 17401 |
| sweep_run.log | 6c47df10794f79e2784e318459401a7c184df9c1fc15671c143b982688e928c8 | 9537 |

Digests computed at publication time from the
files as copied from the originating workspaces;
the originating circuits' packets (included) are
the claim documents for these artifacts.
