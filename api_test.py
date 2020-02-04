import requests
import logging
import json
import api

API_URL = "http://cognition-srv1.ouc.ac.cy/nvt/webservice/api.php"

USER1_UID = 'telegram_130870321'
USER1_NAME = 'Federico'

USER2_UID = 'b2f8711c-3f29-4324-b939-a3d8ddda6fa3'
USER2_NAME = 'Fede_Web'

EID_1 = 94
EID_1_VALID_ANSWERS = 'bark|pet|animal|flea|canine|puppy|cat|woof|bark|tail|wolf|cat|friend|cat|fleas|Dog|beagle|puppy|barking|cat|animal|bone|four|house|legs|best|domestic|pet|god|puppy|pup|mammal|bite|slang|corgi|cur|canine|chap|griffon|Joy|lapdog|Leonberg|Newfoundland|pooch|pug|spitz|flag|fed|loved|it|ker|pasji|pasji|pas|progoniti|psina|ca|gos|hund|vovhund|vovse|andiron|cad|frank|frump|pawl|chase|can|perro|or|tipo|txakur|zakur|kaveri|koira|chien|can|cane|anjing|orang|bisk|hund|pieron|pierun|pies|cachorro|household|god|fox|furry|cat|bark|barks|kennel|mans|backwards|cat|wolf|family|fur|swim|paws|bow|dare|hound|lulu|dogaholic|bonedog|bulldog|chilidog|curdog|dogballs|dogdraw|dogear|dogeared|dogend|dogfood|dogfur|doghead|dogleg|dogrobber|dogshit|dogsitter|dogsled|dogsledder|dogspike|dogtooth|dogwhip|firedog|hangdog|horndog|longdog|sheepdog|sleddog|dogged|dogged|doggie|dogging|doggo|doggy|underdog|Dog|Dog|bitch|dogo|dogue|Dog|Dog|Q144|Dog|Q500936|doge|dogg|dogged|doggest|doggeth|dogging|dogs|dogs|dogs|derogatory|geordie|poker|argot|astronomie|zoologie|british|nautical|overlip|bichon|comhartaich|tabhannaich|akita|basenji|basset|beagle|bloodhound|Bob|borzoi|boxer|briard|Brownie|bulldog|chow|collie|coonhound|cur|cur|dachshund|dalmatian|deerhound|dingo|quadriped|canid|canine|canis|mammal|elkhound|Fido|greyhound|greyhound|Groenendael|harrier|husky|keeshond|koolie|kuvasz|lapdog|malamute|mastiff|pointer|poodle|puli|puppy|puppy|retriever|rottweiler|samoyed|schipperke|setter|sheepdog|sheepdog|shepherd|shetland|spaniel|terrier|vizsla|watchdog|weimaraner|whippet|bitch|hound|legs|adia|alemos|hond|bicce|docga|hunden|hund|tife|xewa|can|perru|kiez|ki|ca|gos|gossa|ayam|ido|iro|itoy|kato|libon|libonon|tukoy|konak|awal|ofi|ghjacaru|it|pes|ci|hund|atze|haufen|haushund|hecheln|hundehalter|hundeleben|hund|lefze|rute|schweinehund|welpe|zibbe|cun|pjas|cortois|hont|avu|africanis|aidi|alco|alsatian|antidog|apricot|aroo|atipamezole|baby|baiting|bandog|bankhar|barbet|barghest|barkese|bark|basenji|baskervillean|bawty|bearhound|bedog|bench|bitch|bitser|boarhound|borzoi|bowser|boy|buansuah|bulldog|canicide|canid|caniform|canine|canine|caninophile|caniphobia|canivorous|canophilia|canophilist|catmill|cavachon|cefovecin|cerberus|chiengora|chihuahua|chiweenie|chondrodystrophoid|choodle|chug|coachdog|cocker|collie|conchectomy|coonhound|corgi|courser|coursing|coydog|creeper|crocotta|crotch|cur|cyanthropy|cynanthropy|cynarctomachy|cynical|cyno|cynocephalic|cynocephaly|cynologist|cynology|cynomorphism|cynophile|cynophilist|cynophobia|cynophobic|cynorexia|dachshund|debark|deerhound|demiwolf|deracoxib|dhole|dirlotapide|dobermann|doga|dogcatcher|cynomorphic|cynomorphism|digital|graphic|on|screen|dogcow|dogdom|dogdraw|dogeater|dogese|dogfucker|doggess|doggily|dogging|doggo|doggy|doghole|doghood|dogitude|dogleg|dogless|doglet|doglike|dogling|doglore|doglover|dogly|dogly|dognap|bitch|click|coward|domesticated|dull|dust|foot|fox|galaxy|girl|horny|human|log|mammal|man|obscured|pallet|ratchet|unattractive|underdog|windlass|wolf|woman|years|bide|cageot|chien|four|galaxie|gars|homme|laideron|mec|navet|obscurcir|pitou|dogness|dogophile|dogote|dogproof|dogproof|dogship'.split('|')

EID_2 = 95
EID_2_VALID_ANSWERS = "nest|chicken|animal|duck|chick|canary|flying|wings|egg|crow|owl|creature|feathers|quail|feathered|Auk|Gull|bat|pigeon|nest|winged|dove|avian|beak|fly|fly|Cardinal|Chickadee|Partridge|Toucan|crow|wren|sparrow|sky|Albatross|archaeopteryx|archaeornis|meat|carinate|cock|dickeybird|hen|hummingbird|nester|passerine|poultry|protoavis|Quetzal|ratite|Roadrunner|Sinornis|trogon|twitterer|Vulture|wildfowl|observe|beak|bird|drumstick|feather|furcula|giblet|hindquarters|oyster|pennon|syrinx|uropygium|wing|wishbone|boo|dame|shuttlecock|ptica|nests|hawk|stork|robin|air|fowl|flyer|mammal|flies|falcon|hawk|hummingbird|kingfisher|nightjar|pelican|plover|swift|wing|nightingale|has|robin|eagle|cardinal|flight|crane|loon|chicken|feathery|birdbrain|birdbrained|birdcage|birdcall|birdcatcher|birdcatching|apostlebird|birdbox|birdcare|birdfeed|birdlife|birdnapper|birdseller|birdshop|birdshot|birdspotter|birdspotting|birdwatcher|birdwatching|birdwoman|blackbird|cedarbird|cockbird|cowbird|dollarbird|gaolbird|hummingbird|moundbird|mousebird|ovenbird|skunkbird|surfbird|thunderbird|warbird|weaverbird|whipbird|whirlybird|wirebird|yellowbird|birder|birder|birdfood|birdhouse|birdie|birdie|birdied|birdieing|birding|birding|birdlet|birdlike|birdlime|birdlimed|birdlimer|birdlimes|birdliming|birdlover|birdloving|birdly|birdman|birdo|birdseed|birdseller|birdshot|birdsong|birdstore|birdstrike|birdwatcher|birdwatching|birdwoman|birdy|birdy|dickeybird|gamebird|hummingbird|seabird|shorebird|waterbird|Bird|Bird|Q5113|Bird|Q26120|birb|birded|birds|birds|cranoc|schwirren|ireland|slang|uk|us|argot|irlande|oiseaux|philippines|essorant|propygostylar|quezal|speight|tika|talitiainen|talitintti|nibli|albatras|gollan|troghan|trogh|baba|garan|gruya|parus|vanagas|falk|haavke|kraan|swalla|noachtegoal|oadeler|oande|dik|eagle|flamingo|stork|albatross|auk|Barbet|animal|dinosaur|amniote|animal|biped|vertebrate|blackbird|Bobwhite|Booby|Bowerbird|Bulbul|Bunting|Buzzard|Canary|cassowary|chickadee|chicken|Cockatiel|colymbiformes|Condor|Coot|coot|Cormorant|Cowbird|crane|crane|crow|crow|Cuck|Cuckoo|cuckoo|cuckoo|Curassow|dodo|dove|dove|dove|eagle|eagle|Eidar|emu|finch|finch|Flycatcher|flycatcher|fowl|galbuliformes|Gannet|gerfalcon|goldfinch|grackle|Grebe|grouse|hawk|hoatzin|Hornbill|huia|hummingbird|hummingbird|Ibis|ibis|ibis|jackdaw|Jay|Kestrel|kingfisher|kingfisher|Kite|kittiwake|kiwi|kookaburra|loon|Lorikeet|Lovebird|Magpie|Mallard|Martin|mockingbird|mockingbird|mousebird|nightingale|Nightjar|nightjar|ortolan|Osprey|ostrich|ovenbird|Owl|owl|owl|Oxpecker|palila|parrot|parrot|parrot|passerine|peacock|pelican|pelican|penguin|penguin|Petrel|petrel|petrel|pheasant|pheasant|Pigeon|pigeon|pigeon|pigeon|plover|plover|puffin|Rail|raptor|raven|raven|Rhea|rhea|robin|rook|Sapsucker|seabird|seiurus|skylark|sparrow|starling|stilt|Stork|stork|stork|swallow|swallow|Swift|tern|Thrasher|Thrush|thrush|thrush|Tinamou|titmouse|toucan|trogon|turkey|tweety|vireo|vulture|vulture|Wagtail|wagtail|Warbler|warbler|waterfowl|Waxwing|Weaver|woodpecker|woodpecker|wren|kimbiro|sips|au|chincharana|fleogenda|fugol|paxaro|evn|labous|au|ocell|chisti|bilitsina|bunhok|ekek|goryon|iti|iyak|kukok|kuyabog|langgam|paripari|pispis|piyak|sungo|wakwak|yapyap|machang|wikikmal|foshi|kunda|vlhovec|adar|edn|fugl|flucht|harpyie|laufvogel|mauser|nachtvogel|sommervogel|vogelkot|vogelkunde|vogel|vogelnest|vogelsang|wintervogel|zugvogel|paserain|vogel|xe|xevi|accipitrine|adjutant|adzebill|agami|akalat|akekee|akepa|albuminin|alcid|allantois|allopreening|altrices|amniote|amphikinesis|anhima|anhinga|animal|ani|anisodactylous|anisodactyly|anseriform|antestomach|antiavian|antibird|anting|antitrochanter|antpipit|anvil|apterium|archeopteryx|articulary|asity|auchenium|auriculars|auspicate|auspice|autophagi|avialan|avialian|avian|avianlike|avian|avi|avicidal|avicide|avicolous|avicular|aviculture|aviculturist|avidin|avifauna|aviform|aviphile|avipoxvirus|avisodomist|avisodomy|avivore|avoset|avulavirus|aylet|babbler|baby|bananaquit|barbet|basipodium|batfowling|beak|beard|beefeater|berrypecker|bicalcarate|birdbath|birdbolt|birdcage|birdcall|birdcare|birdcatcher|birdcatching|birddom|birder|birdfeeder|birdfeed|birdhood|birdie|birdikin|birdish|birdkeeper|birdkeeping|birdless|birdlessness|birdlet|birdlike|birdling|birdlore|birdlover|birdly|birdman|birdmom|birdnap|airplane|animal|attractive|aves|birb|burd|chicken|chirp|chordata|class|eaglet|egg|feather|fellow|flight|fowl|man|nestling|penis|phylum|satellite|sentence|squawk|tweet|wing|attractif|femme|gonzesse|individu|meuf|nana|oiseau|poule|prison|taule|type|birdness|birdproof|birdseller|birdshop|birdsit|birdskin".split('|')

EID_3 = 96
EID_3_VALID_ANSWERS = "milk|animal|milk|moo|bovine|farm|beef|bull|horse|udders|udder|cattle|mammal|farm|milk|cattle|placental|heifer|springer|poll|udder|jalovica|krava|kravlji|vaca|ko|krava|overawe|vaca|vaquita|behi|vache|mucca|vacca|vaccina|lembu|ku|krowa|prukwa|vaca|steer|ox|farms|black|calf|dairy|producer|milking|giver|sacred|gives|animal|steak|heifer|white|bull|bull|Cow|cowgirl|cowbell|cowboy|cowcatcher|coward|cowbane|cowbird|cowcatcher|cowdung|cowgal|cowhand|cowherb|cowherder|cowkeeper|cowlick|cownose|cowpat|cowpath|cowpea|cowpock|cowpoke|cowpony|cowpooling|cowpuncher|cowshed|cowtown|cowgirl|cowhand|cowherd|cowhide|cowman|cowmilk|cowpat|cowpoke|cowpool|cowpuncher|cowshed|cowshit|kou|kau|Cattle|Cattle|cowed|cowed|cowing|cowing|cows|cows|cows|cows|kine|kye|ky|computing|biology|derogatory|dialect|formerly|inexact|mining|properly|uk|zoologie|aurochs|bovine|buffalo|adult|ruminant|cattle|laa|kaoziia|kaoz|bees|koei|cu|neat|waka|vaca|vaca|waka|baka|kou|vaaka|wak|karwa|buwch|ko|kue|muhko|fresser|kuh|kuhwiese|milchkuh|rind|schweizer|baca|busca|gowjedo|krowa|coe|rint|enyi|agglutinin|anticow|bail|beefalo|beefer|beef|boanthropy|boose|bossy|bovicide|bovine|brie|buffalopox|bulling|buttermilk|caerphilly|calf|calver|cammocky|carcake|cattle|chuck|clap|cleaning|cowbell|low|ox|veal|cowdom|cowdung|cowed|cowest|coweth|cowfoot|cowheel|cowhouse|cowing|cowleech|cowless|cowlike|cowling|cowmilk|adult|age|beef|bovid|bovine|brake|buffalo|bull|calf|calved|car|chimney|chock|cowl|difficult|elephant|fat|female|food|hippo|lazy|machine|mammal|manatee|meat|moose|nasty|rhino|seal|sex|species|stupid|unpleasant|wedge|whale|woman|yak|garce|vache|cowness|cowpath|cowpat|cowpie|cowplop|cowpooling|cowpool|cowpool|cowshed|cowshit|cowskin|cows|cows|intimidate|effrayer|intimider|terrifier|cowy|cowyard|daisy|damona|danbo|disbudding|dogcow|dogie|dung|dzo|escutcheon|fardingbag|foremilk|friesian|garget|gobar|gorgonzola|goshala|hathor|hawkie|headstock|heifer|herdsman|herdswoman|jersey|jersian|jibbings|jomo|kaymak|kie|kilishi|kine|laystall|leppy|manure|mess|milker|milk|mombie|moo|mooey|moo|morbier|mozzarella|mulley|neat|nkwobi|noncow|noncow|overawe|oxtail|reticulum|retrovaccination|rodeo|ruminant|scur|setter|sole|sook|spean|stirk|strapper|stripper|strippings|strip|strokings|throw|tulchan|udderly|vacci|vaccicide|vaccimulgence|wagasi|wagon|werecow|whethering|yakow|alkino|bovinejo|bovino|bovo|elefantino|guno|muu|sireno|becerro|mugido|ternero|vaca|vaqueriza|vaquerizo|vaquita|lehm|behi|nagge|itikka|baka|bulo|lehmi|lehmihaka|guya|nauta|nuti|kusa|chipie|fourme|maroilles|beuf|vache|buef|vache|pourriture|putain|rosse|vache|velle|vacje|ko|agh|bainirseach|bearach|liath|odhar|agh|bacadh|gamhainn|mart|sgrogag|vaca|kuo|chue|booa|saniya|pipi|baka|duyong|kruwa|vacca|bovino|bovo|elefantino|baula|belja|kusa|mykja|skepna|intimorire|mucca|scamorza|vacca|vaccareccia|vacchino|vaccino|mori|lehmy|mange|bugh|buwgh|bos|bovatim|bovillus|bovinus|bubulus|bucetum|burra|ceva|vaka|forda|iumentum|iunix|iuvenca|vacca|vaccinatus|vaccinus|vitula|kou|rand|niem|vacia|saitas|govs|tele|omby|kau|sapi|baqra|vufera|huacax|vacas|koh|brommer|koebeest|koeienhandel|koe|koevoet|kol|kween|zeug|kua|ku|ko|vacque|vak|vaque|kuo|flaki|krasula|krowa|wakash|bezerra|vaca|waka|vacca|vacha|vatga|bacca|coo|yeld|gussa|ag|dam|krava|govedo|krava|kuss|sac|troke|ku|kalva|ko|kossa|mu|sygyr|bulmakau|kau|inek|keu|sigir|buasa|malga|vaca|vacaro|lehm|bubamit|bub|jigiraf|kunamilig|kun|baka|vatche|nag|ko|ingoqokazi|inhlamvukazi|inkomo|insizwakazi|isigedlekazi|umalukazi|umhlophekazi|manga|bull|browbeat|bully|koei|baca|cu|waka|vaca|misi|vaca|waka|vacca|tuvar|karwa".split('|')

EID_4 = 97
EID_4_VALID_ANSWERS = "animal|trout|water|sea|creature|ocean|swimming|Fish|gills|scales|Fish|scales|scale|fins|swimmer|food|Fish|Hunger|wait|aquatic|trout|trout|carp|salmon|bass|underwater|minnow|Fish|Fish|Fish|list|alewife|anchovy|fingerling|food|Fish|goldfish|Grouper|haddock|hake|mouthbreeder|mullet|panfish|schrod|shad|smelt|spawner|stockfish|trout|angle|brail|crab|catch|search|prawn|rail|scallop|seine|shark|shrimp|trawl|fin|fishbone|milt|roe|pisces|Fish|visk|riba|swim|shark|marine|swims|has|eel|haddock|herring|scaly|shark|sardine|dweller|sea|ocean|animals|tuna|seafood|mermaid|life|bass|haddock|bones|Fish|Fish|Fish|Fish|Fish|Fish|Fish|Fish|Fish|Fish|Fish|fishermen|summer|fishability|bandfish|barrelfish|bellowfish|billfish|blindfish|broodfish|candlefish|cavefish|clingfish|coalfish|cofferfish|combfish|cornetfish|crabfish|crampfish|crestfish|cucumberfish|dartfish|dragonfish|driftfish|fishball|fishboat|fishbolt|fishbone|fishbowl|fishcake|fishcatcher|fishfinder|fishfly|fishgarth|fishhawk|fishline|fishmouth|fishnet|fishpole|fishtank|fishway|fishwort|flagfish|frostfish|gamefish|garfish|goldfish|greenfish|guitarfish|hagfish|hairyfish|icefish|inkfish|jawfish|knifefish|lanternfish|leaffish|lumpfish|lungfish|oarfish|oilfish|paddlefish|panfish|paradisefish|parrotfish|pipefish|pufferfish|saltfish|sandfish|shorefish|snailfish|snakefish|spadefish|spearfish|squirefish|suckfish|swordfish|telescopefish|threadfish|threefish|toadfish|tonguefish|torrentfish|towfish|trunkfish|velvetfish|wallfish|weaverfish|weeverfish|fishen|fisher|fishie|fishing|fishlike|fishy|fisc|fiscian|fisch|fiche|ufishi|Fish|Fish|Q152|Fish|Q317441|fished|fished|fishes|fishes|fishes|fishest|fishes|fisheth|fishing|fishing|ghoti|Fish|Fish|oceans|roue|piranha|charr|chavender|chevin|chogset|codless|astrology|astronomy|derogatory|loosely|nautical|slang|zoology|cricket|nautical|glossohyal|gravelling|inconnue|pauhagen|poghaden|pogy|run|sandre|snakehead|bagre|barracuda|bonito|escombro|morena|sierra|appelsiinipleko|kylkiviiva|suutari|sciata|fleogan|escarapote|bleayst|desostizar|vakuigar|pullulare|las|aal|lieu|sole|faren|buy|Fish|Fish|Fish|cast|kipper|sole|anglerfish|arapaima|barracuda|barracuda|barreleye|blobfish|carp|catfish|cephalaspidomorphi|channichthyidae|cod|codfish|dolphin|eel|eel|eulachon|animal|Fish|Fish|Fish|Fish|purdy|rad|seafood|Fish|Fish|animal|meat|seafood|vertebrate|flatfish|halibut|herring|herring|kipper|mackerel|mackerel|mackerel|marlin|minnow|monchong|opah|opakapaka|pahrump|pike|pirana|plaice|plaice|salmon|salmon|salmon|seafood|shark|shark|Snapper|spikedace|sturgeon|swordfish|tilapia|toro|trout|trout|tuna|tuna|tunny|tunny|walleye|woundfin|cooked|eaten|Fish|Fish|marinated|namasiia|namas|vis|fiscian|fisc|pescar|pexe|pesk|moll|peix|pescar|awachi|bangus|bulad|buwad|dayok|eskabetse|isdaa|isda|karaho|kinilaw|kugtong|mamasol|mamukot|managat|mangisda|mulmol|pasol|pukot|taga|tuloy|ukoy|iik|kiyul|visch|sazan|ryba|pysgod|aborre|fiske|fisk|angeln|aquarienfisch|backfisch|fischbecken|fischbestand|fischen|fischfressend|fisch|fischreich|meeresfisch|milch|salzwasserfisch|zierfisch|pasc|ryba|visch|visschen|rm|sbnw|aba|acanthodian|acanthomorph|acousticolateralis|actinopterygian|actinost|actinotrichium|adelphophagy|adnate|akutaq|alampy|albacore|alburn|alepidote|alevin|alfione|allice|alligatorfish|alosid|amberjack|ammodyte|anabantoid|anableps|anacanthous|anadrom|anadromy|andropodium|angler|angle|angleworm|anhinga|animal|anisakiasis|anthia|antifish|aquaculture|aquariist|aquarium|arapaima|archerfish|arista|arthrodiran|arthrodire|articulary|asp|atherine|aulopiform|autopalatine|bab|bachelor|backfin|backtroller|backtroll|bagoong|bait|balachong|balistoid|balloonfish|ballotine|bandfish|bangda|bannerfish|banstickle|barbel|barreleye|bashaw|basipterygium|basslet|bathydemersal|batrachoid|beachsalmon|beakfish|beardfish|beard|becker|becuna|bellowsfish|beluga|berry|beryciform|berycoid|bignose|billard|billfish|birt|bisque|blacken|blacksmith|blacktail|blancmange|blancmanger|bleak|blennoid|blindfish|blobfish|blob|blower|blowfish|blueback|bluefish|bluehead|bluestripe|bolty|bonaci|bone|boning|bonito|boxfish|bradyodont|braize|branchio|branchiostegal|branlin|bristlemouth|brochette|broggle|bryconin|bubbler|bufonite|burbot|burfish|burgall|burley|burrock|bycatch|cabrilla|cackerel|cade|callop|candiru|candlefish|carangid|carangiform|carangoid|caranx|carbonado|cardinal|carp|carpsucker|catalufa|catchability|catfish|cauf|cavally|cavefish|cephalaspidomorph|chanpuru|characiform|characin".split('|')

EID_5 = 98
EID_5_VALID_ANSWERS = "animal|riding|pony|equine|mammal|saddle|racing|mane|big|donkey|farm|four|zebra|large|ride|legs|race|hooves|jockey|cow|tail|pony|hay|ride|ridden|bay|chestnut|eohippus|hack|mesohippus|pacer|palomino|pinto|protohippus|racehorse|roan|sorrel|stablemate|steeplechaser|stepper|workhorse|provide|remount|encolure|gaskin|horseback|horsemeat|poll|withers|at|centaur|hackney|ajam|jarac|konj|krkalina|krkalo|mrkov|sivac|struna|vranac|cavall|hest|hyphest|pruhest|ross|cavalry|knight|sawhorse|peerd|konj|caballo|zaldi|hevonen|voimisteluhevonen|cheval|cheval|cheval|peste|cabalo|cavallo|kuda|kuda|hest|cavalo|cavalos|neigh|stallion|derby|equestrian|cowboy|saddle|mule|mare|races|cowboys|kentucky|fast|racer|transportation|mule|steed|animal|mare|bit|long|hay|carriage|forehorse|horseback|boathorse|carthorse|coachhorse|darkhorse|henny|horseback|horsebox|horsecollar|horsedung|horsefly|horsehair|horsekeeper|horselaugh|horseperson|horsepower|horsepox|horseriding|horseshoer|horsetail|horsetrade|horsetrader|horsetrading|horseway|horsewhip|packhorse|ploughhorse|plowhorse|racehorse|whitehorse|horsedrench|horseflesh|horsefly|horsegate|horsekind|horseless|horselike|horseman|horsemanship|horseplay|horsepower|horseradish|horseshit|horseshoe|horsewear|horsewhip|horsey|horsie|horsy|racehorse|unhorse|unhorse|hoi|hors|ihhashi|Horse|Horse|Q482443|Q726|Horse|horsed|horsed|horsen|horses|horses|horses|horses|horsing|horsing|angkas|mustang|chess|historical|military|mining|nautical|slang|us|zoology|zoologie|lyard|dresser|entabler|entretailler|ferrare|lyart|phi|ass|mare|pony|zebra|burro|colt|donkey|donkey|filly|foal|foal|gelding|gelding|hinny|Holly|ore|animal|equine|mammal|mammal|mare|mare|Moses|mule|Nibbles|pony|pony|stallion|stud|yearling|zebra|colt|foal|mare|pony|stallion|yearling|perd|ruiter|caballo|blanca|eoh|hengest|hors|mearh|stod|wicg|kawej|caballu|cavall|kawali|alasan|kabayo|tigidig|arus|kavaayu|pasukat|issoba|carfil|ceffyl|march|ekvipage|hest|fiaker|gaul|huf|kobel|kracke|ostfriese|pferd|rappe|reiten|reitpferd|ross|schimmel|spiegel|stute|cavul|draf|pert|somer|ssm|ssmt|acceptance|alicorn|amble|ambler|anbury|andalusian|anticor|antihorse|appaloosa|arabian|arab|arrastra|attaint|avener|aver|backband|ballotade|barbel|barb|bard|barnacle|bar|base|bathorse|bayard|bay|beard|bellyband|bidet|bishop|bleyme|blinkers|bloodstock|blossom|boathorse|boggard|brake|breeching|bricole|bridle|brills|broncobuster|bronco|broomtail|browband|brumby|bucephalus|bucker|bucket|buckjumping|bullet|burdon|butteris|caballine|cadence|calade|canker|canter|canuck|capellet|capel|caple|capriole|career|car|carney|carthorse|cast|cataphract|cattle|cavesson|cayuse|chambon|chamfron|chanfrin|chaperon|charbon|chariot|chaunter|checkrein|chestnut|cheval|claybank|cleft|clop|coachfellow|coachhorse|coachwheel|coachwhip|cocktail|colthood|colt|colt|conquest|coronary|countermark|counter|countertime|courbette|crapaudine|creamy|crepance|crest|cribbing|crinet|criniere|crock|cronet|cropout|croupade|croupiere|croup|croupon|crowbait|crupper|curple|currycomb|curvet|daubing|demivolt|dennet|dermatosparaxis|detomidine|dishorse|dobbin|dongola|donkey|dragoon|dragsman|dressage|dumminess|eatage|ectoloph|encolure|epona|equestrianism|equid|equilin|equine|equinism|equinophobia|equitant|equuleus|estrapade|evener|eventer|eyeflap|falcade|famine|farcied|farcy|farrier|fartknocker|favel|feague|feather|fetlock|fettler|figging|filly|finnhorse|finnikin|flunixin|flynet|foal|footcloth|footguard|forefoot|forehand|forehorse|foretop|fourchette|friesian|frog|frommarding|frush|gainage|gallop|galloway|gambade|gambrel|garron|gaskin|gee|gee|gelding|genet|gibber|gigster|girning|glanders|glasseye|glome|glossanthrax|goer|goey|grape|grasscutter|grey|groundline|grullo|gytrash|hack|hackneyman|haircloth|haras|harnessmaker|hayrake|headcollar|headgear|heaves|hinny|hippiater|hippiatrist|hippiatry|hippic|hippocamp|hippo|hippocephalic|hippogriff|hippoid|hippolith|hippologist|hippology|hippomancy|hippomania|hippomorphic|hippopathology|hippophagist|hippophile|hippophilia|hippophilic|hippophobe|hippophobia|hippophobic|hippotomy|hitchrack|hitchrail|hobday|hog|holsteiner|hoofbound|hoof|hoofstock|hopple|horseboat|horsebound|horsebox|horsebreaker|horsebreaking|horsecar|horsecart|horsecloth|horsecollar|horsedealer|horsedung|horsed|horseflesh|horsehair|horsehood|horsekeeper|horsekind|horseless|horselike|horseling|horseload|horselore|horsely|horseman|horsemanship|horsemeat|horsen|aid|animal|antidepressant|anxiolytic|approximately|ass|basketball|breastband|brumby|cavalry|charger|colt|equid|equidae|equipment|equus|examination|extinct|family|filly|footrope|frame|furling|gallop|gee|gymnastics|heroin|hoof|horseplay|illegitimate|jackstay|knight|leadsman|leg|mammal|mare|morphine|neigh|palfrey|pony|reefing|ride|rope|sedative|soldier|soldiers|stallion|study".split('|')

def assert_equality(a, b):
    assert a == b, "{} != {}".format(a, b) 

def random_string_generator(size):
    import random
    import string
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(size))

def test_random_answers():
    api.add_user(USER1_UID, USER1_NAME)
    new_answer = random_string_generator(15)
    json_response = api.store_response(EID_1, USER1_UID, new_answer)
    assert_equality(json_response["userid"], USER1_UID) 
    assert_equality(int(json_response["eid"]), EID_1) 
    assert_equality(json_response["response"], new_answer) 
    assert_equality(json_response["points"], None) 

def test_valid_answer():
    api.add_user(USER1_UID, USER1_NAME)
    valid_answer = EID_1_VALID_ANSWERS[0]
    json_response = api.store_response(EID_1, USER1_UID, valid_answer)
    assert json_response["points"] > 0, '{} <=0 {}'.format(json_response["points"], 0)
    json_response = api.store_response(EID_1, USER1_UID, valid_answer)
    assert_equality(json_response["points"], 0) 

def test_notifications():
    api.add_user(USER1_UID, USER1_NAME)
    response_json = api.get_user_info(USER1_UID)
    print(json.dumps(response_json, indent=3))
    api.add_user(USER2_UID, USER2_NAME)
    response_json = api.get_user_info(USER2_UID)
    print(json.dumps(response_json, indent=3))
    new_agreed_answer = "new agreed answer"
    print("Agreed answer: {}\n".format(new_agreed_answer))
    api.store_response(EID_1, USER1_UID, new_agreed_answer)
    api.store_response(EID_1, USER2_UID, new_agreed_answer)
    api.store_response(EID_1, USER1_UID, random_string_generator(15))
    api.store_response(EID_1, USER1_UID, random_string_generator(15))
    api.store_response(EID_1, USER1_UID, random_string_generator(15))    
    api.store_response(EID_1, USER1_UID, random_string_generator(15))   
    # at least 6 
    # json_response = api.get_notifications(USER1_UID)
    # print("Notifications first call: {}\n".format(json.dumps(json_response, indent=4)))
    # json_response = api.get_notifications(USER1_UID)
    # print("Notifications second call: {}\n".format(json.dumps(json_response, indent=4)))
    # json_response = api.get_notifications(USER1_UID)
    # print("Notifications third call: {}\n".format(json.dumps(json_response, indent=4)))

def test_user_info():
    response_json = api.get_user_info('invalid_user')
    print(json.dumps(response_json, indent=3))
    assert len(response_json)==0
    response_json = api.add_user(USER1_UID, USER1_NAME)
    print("Add user response:\n{}".format(json.dumps(response_json, indent=3)))
    response_json = api.get_user_info(USER1_UID)
    print(json.dumps(response_json, indent=3))
    assert len(response_json)>0

def test_get_exercise():
    api.add_user(USER1_UID, USER1_NAME)
    exercise_json = api.get_exercise(USER1_UID) #elevel='A1', etype='LocatedAt'
    print("Exercise response:\n{}".format(json.dumps(exercise_json, indent=3)))

def test_choose_exercise():
    api.add_user(USER1_UID, USER1_NAME)
    response_json = api.choose_exercise(USER1_UID)
    print("Exercise response:\n{}".format(json.dumps(response_json, indent=3)))

def test_get_close_exercise():
    api.add_user(USER1_UID, USER1_NAME)
    exercise_json = api.get_close_exercise(USER1_UID) #, elevel='A1', etype='RelatedTo' #RelatedTo, LocatedAt
    print("Exercise response:\n{}".format(json.dumps(exercise_json, indent=3)))
    store_response_json = api.store_close_response(exercise_json['eid'], USER1_UID, 2)
    print("Exercise store response:\n{}".format(json.dumps(store_response_json, indent=3)))

def test_get_close_exercise_multi(): 
    for i in range(1000):
        if i%10 == 0:
            print('\r{}'.format(i))
        exercise_json = api.get_close_exercise(USER1_UID) #, elevel='A1', etype='RelatedTo' #RelatedTo, LocatedAt
        assert(exercise_json is not None)

def test_random_response():
    api.add_user(USER1_UID, USER1_NAME)
    exercise_json = api.get_exercise(USER1_UID)
    eid = exercise_json['eid']
    #exercise = exercise_json['exercise']
    random_response_json = api.get_random_response(eid, USER1_UID)
    print("Random response:\n{}".format(json.dumps(random_response_json, indent=3)))

def test_leaderboard():
    leaderboard_json = api.get_leaderboard()
    print(json.dumps(leaderboard_json, indent=3))    
    
    

if __name__ == "__main__": 
    #api.reset_db()
    
    #test_user_info()
    #test_random_answers()
    #test_valid_answer()
    #test_notifications()
    # test_get_exercise()
    #test_leaderboard()
    #test_random_response()
    # test_choose_exercise()
    # test_get_close_exercise()

    
    test_get_close_exercise_multi()