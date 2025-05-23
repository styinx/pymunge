def fnv1a_32(s: str) -> int:
    """
    Customized `fnv1a (32-bit variant) algorithm <https://en.wikipedia.org/wiki/Fowler–Noll–Vo_hash_function>`_.
    Converts unsigned 32 bit integer hash from the input string.
    The input string is converted to lowercase () while hashing.

    :param str s:   The input string.

    :return:        The calculated hash value.
    :rtype:         int
    """
    h = 0x811C9DC5
    for c in s:
        h = (h ^ (ord(c) | 0x20)) * 0x1000193
        h &= 0xFFFFFFFF  # emulate 32-bit overflow
    return h


KEYS = {
    # ODF Section
    'ExplosionClass': 0xca0c1378,
    'GameObjectClass': 0xd3dd9cec,
    'InputSystem': 0xc21867e2,
    'InstanceProperties': 0x7c4ab7df,
    'OrdnanceClass': 0xd59a9357,
    'Properties': 0x11de6cdc,
    'WeaponClass': 0xacda90ab,

    # ODF Key
    'abandon': 0xcacdfee6,
    'Acceleration': 0x2fa0ba9d,
    'Acceleraton': 0x9f8a0040,
    'AcquiredTargetSound': 0x399ee477,
    'ActiveRotateNode': 0x2c70cf18,
    'ActiveSpinNode': 0x18275a73,
    'AddHealth': 0x3f9ab262,
    'AddonAttachJoint': 0xa423e008,
    'AddShield': 0xbad94c15,
    'AddShieldOff': 0x729dfa7a,
    'AddSpringBody': 0x5f1b7721,
    'AfterburnerOffSound': 0x81cd3487,
    'AfterburnerOnSound': 0xc6070f55,
    'AfterburnerSpeed': 0x1653e576,
    'AIDriverGetInSound': 0x0f514ef3,
    'AIDriverGetOutSound': 0xe715f1e0,
    'AIFieldFollowSound': 0x13701ff3,
    'AIFieldHoldSound': 0x68d19d53,
    'AIFieldMoveOutSound': 0x775fc11b,
    'AIGunnerAllClearSound': 0x7713e78f,
    'AIGunnerGetInSound': 0x558bfe36,
    'AIGunnerGetOutSound': 0x5b09376b,
    'AIGunnerSteadySound': 0x7c2f5ca1,
    'AimAzimuth': 0x3186fbfe,
    'AimDistance': 0xecdb9d1d,
    'AimElevation': 0x8339fb35,
    'AimerNodeName': 0xc182abc2,
    'AimerPitchLimits': 0x2d6487bd,
    'AimerPitchLimts': 0x0f5fd13c,
    'AimerYawLimits': 0xa9c3675c,
    'AimerYawLimts': 0xb5c7341b,
    'AimFactorMove': 0xa5f0bee0,
    'AimFactorPostureCrouch': 0xc7898205,
    'AimFactorPostureProne': 0x13ffe717,
    'AimFactorPostureSpecial': 0x639c75ce,
    'AimFactorPostureStand': 0x497c03a9,
    'AimFactorStrafe': 0x95a83c02,
    'AimTension': 0x5e3171cc,
    'AimValue': 0xa5e1e577,
    'AIPassengerGetInSound': 0x27fd5753,
    'AIPassengerGetOutSound': 0xcd2c33c0,
    'AIPassengerMoveOutSound': 0x2c2c6d07,
    'AIPassengerStopSound': 0xe1828f44,
    'AIResponseNosirSound': 0xcec0e772,
    'AIResponseYessirSound': 0xc44afaae,
    'AISCDriverGetInSound': 0xe0999151,
    'AISCDriverGetOutSound': 0x3b62b992,
    'AISCFieldFollowSound': 0x1d988641,
    'AISCFieldHoldSound': 0x8018b09d,
    'AISCFieldMoveOutSound': 0x150a38e9,
    'AISCGunnerAllClearSound': 0x22987695,
    'AISCGunnerGetInSound': 0x7ef094d0,
    'AISCGunnerGetOutSound': 0xdf526f61,
    'AISCGunnerSteadySound': 0x1aec5f13,
    'AISCPassengerGetInSound': 0xf9d92705,
    'AISCPassengerGetOutSound': 0x45912fae,
    'AISCPassengerMoveOutSound': 0x2512bb6d,
    'AISCPassengerStopSound': 0xa473e5ea,
    'AISCResponseNosirSound': 0x60681218,
    'AISCResponseYessirSound': 0x8e131444,
    'AISizeType': 0xaff22806,
    'AlignVertical': 0xdb873344,
    'AllMusic': 0x4232e9bf,
    'AllyCount': 0x7136fd3e,
    'AllyPath': 0xdad215b0,
    'Alpha': 0x5d8b6dab,
    'Ambient2Sound': 0x9a108b4a,
    'AmbientSound': 0x65a920ba,
    'AnimalHealth': 0x60d746d7,
    'AnimalScale': 0x9aa17a49,
    'AnimatedAddon': 0xe8888b42,
    'AnimatedPilotPosition': 0x11ce2025,
    'Animation': 0xe145ee5d,
    'AnimationAddon': 0xdddcde45,
    'AnimationBank': 0xa7678f8f,
    'AnimationExtraFile': 0x3a714b27,
    'AnimationLowRes': 0x1ecc7e0d,
    'AnimationName': 0x98557a5e,
    'AnimationTrigger': 0x1d56b73b,
    'ApproachingTargetSound': 0xeb6089a1,
    'ArmName': 0x90491ed6,
    'ArmorScale': 0xa0bb60ce,
    'AttachDynamic': 0x51e2c845,
    'AttachedMesh': 0xe90ecacc,
    'AttachEffect': 0x6a6c7e0d,
    'AttachOdf': 0xa9d0d48b,
    'AttachToHardpoint': 0x3be7b80a,
    'AttachToHardPoint': 0x3be7b80a,
    'AttachTrigger': 0x72306628,
    'AutoAimSize': 0x7dbe88fa,
    'AutoAimYLimits': 0xf07b5b62,
    'AutoFire': 0x9d39f68a,
    'AvailableForAnyTeam': 0x0ffe3c06,
    'BallAcceleration': 0xde6b8538,
    'BallCollision': 0x8f720e3c,
    'BallLowResModel': 0x19d9ab85,
    'BallMaxLean': 0xd2da8f5e,
    'BallMinMoveSpeed': 0xed895ee0,
    'BallMoveSpeed': 0xacacdb0c,
    'BallMoveThreshold': 0x09a7a164,
    'BallRadius': 0x9895bb7a,
    'BallRollingFriction': 0x6560de67,
    'BallSlippage': 0xdc524dd9,
    'BallTurnSpeed': 0x578f6ae6,
    'BallWaterDamageHeight': 0xac229931,
    'BankAngle': 0x6d7c9f7e,
    'BankFilter': 0x35de28f1,
    'BarrelLength': 0xef095ea9,
    'BarrelNodeName': 0x1e534b12,
    'BarrelRecoil': 0x5a29d1cb,
    'BeamIntensity': 0x75096fab,
    'BlurEffect': 0xb9282909,
    'BlurLength': 0x9d0fb7a4,
    'BlurStart': 0x04afc6a4,
    'BodyOmegaXSpringFactor': 0xa8a2ecbe,
    'BodySpringLength': 0xeafe81d0,
    'BoostSound': 0x79e2d013,
    'BoxSize': 0x35a4393b,
    'BuildAnimation': 0x2fd8a07b,
    'BuildingAmmo': 0xa25f865f,
    'BuildingBuild': 0x09cc7f53,
    'BuildingCollision': 0x9828f43f,
    'BuildingCollisionPrim': 0x8cf29543,
    'BuildingHealth': 0xa6c59e9f,
    'BuildingRebuild': 0x03ec6220,
    'BuildingScale': 0x02168f61,
    'BUILDINGSECTION': 0xd89b1a5c,
    'BuildModelOdf': 0x138b5187,
    'BuildPoint': 0x619005ab,
    'BuiltCollision': 0x06b4bbb5,
    'BuiltSound': 0x66aab312,
    'CableLength': 0xd9b746b2,
    'CameraDistance': 0x4e2c3b35,
    'CameraHeight': 0x09205fe5,
    'CAMERASECTION': 0xbaca6bf1,
    'CanDeflect': 0xb0d14ce0,
    'CapturedSound': 0xf17a02e6,
    'CapturePosts': 0x325f7c20,
    'CaptureRegion': 0xc6c161f9,
    'CaptureTime': 0xeb1bcbf8,
    'CargoNodeName': 0x3e2c4da4,
    'ChangeModeSound': 0xc77178c1,
    'ChargeDelayHeavy': 0xf303ac7b,
    'ChargeDelayLight': 0x516c9f08,
    'ChargeRateHeavy': 0x60ddbf8e,
    'ChargeRateLight': 0xf5701d6d,
    'ChargeSound': 0x4ee58508,
    'ChargeSoundPitch': 0x12586dae,
    'ChargeUpEffect': 0x18c5f75d,
    'ChunkAngularDamping': 0x0e3bec8e,
    'ChunkBounciness': 0xc2f5ffd5,
    'ChunkDeathSpeed': 0xed35b79b,
    'ChunkFrequency': 0x43b50014,
    'ChunkGeometryName': 0xda328455,
    'ChunkLinearDamping': 0xfeb5ed07,
    'ChunkNodeName': 0xebf014fd,
    'ChunkOmega': 0x166f6939,
    'ChunkPhysics': 0xc8e32dc3,
    'CHUNKSECTION': 0xda1de03d,
    'ChunkSimpleFriction': 0x1cdaebc2,
    'ChunkSmokeEffect': 0xd350c3de,
    'ChunkSmokeNodeName': 0x472e0410,
    'ChunkSpeed': 0x945d1d15,
    'ChunkStartDistance': 0xcd61e401,
    'ChunkStickiness': 0xb94ae34e,
    'ChunkTerrainCollisions': 0x0a157be2,
    'ChunkTerrainEffect': 0x048f1226,
    'ChunkTrailEffect': 0x94f0544b,
    'ChunkUpFactor': 0xc316ae10,
    'ChunkVelocityFactor': 0xb3574d92,
    'CisMusic': 0xaf8e60ed,
    'CISMusic': 0xaf8e60ed,
    'ClankLeftRunSound': 0x1064c0a7,
    'ClankLeftWalkSound': 0xb77f3981,
    'ClankRightRunSound': 0x10a991e4,
    'ClankRightWalkSound': 0xb989fc18,
    'ClassAllATK': 0xdd29eddc,
    'ClassAllDEF': 0x2a456b61,
    'ClassCISATK': 0xa2c909c6,
    'ClassCISDEF': 0x9e973303,
    'ClassHisATK': 0xe2c47a79,
    'ClassHisDEF': 0x9836edac,
    'ClassImpATK': 0x54d2fc8b,
    'ClassImpDEF': 0x07b77f06,
    'classLabelClassLabel': 0x088daa81,
    'ClassLocATK': 0xd92c6ca7,
    'ClassLocDEF': 0xcaa92a12,
    'ClassRepATK': 0x24f75004,
    'ClassRepDEF': 0x61c30279,
    'CloseSound': 0x4fcf4562,
    'ClothingRustleSound': 0x5625fc0b,
    'cmd_lclick': 0x959ebe48,
    'cmd_lhold': 0xd747be1d,
    'cmd_rclick': 0xbde91c2a,
    'cmd_rhold': 0xa311ad53,
    'CockedAngle': 0x64a37d77,
    'CockpitChatterStream': 0x8278705f,
    'CockpitTension': 0x104cd1b8,
    'CodeInitialWidth': 0x6e0ba2d4,
    'CollisionCOLLISION': 0xf082b381,
    'CollisionInflict': 0x2ef03732,
    'CollisionLowResRootScale': 0x6a688deb,
    'collisionName': 0x5397318c,
    'CollisionOtherSound': 0xedc6251a,
    'CollisionRootScale': 0xc64a53ab,
    'CollisionScale': 0x1a87bacf,
    'CollisionSound': 0xc28f0c96,
    'CollisionThreshold': 0x2cdb588a,
    'Color': 0x3d7e6258,
    'ConeAngle': 0xa3f03b49,
    'ConeFadeFactor': 0x857435a7,
    'ConeFadeLength': 0x2c52f680,
    'ConeHeight': 0xeaaaa7a9,
    'ConeInitialWidth': 0x9cbb54e2,
    'ConeLength': 0x9342844e,
    'ConeWidth': 0x6f7f1016,
    'Controllable': 0xb371fc9a,
    'ControlRegion': 0x805c1f8a,
    'ControlZone': 0x447c6db0,
    'CrouchMoveSpread': 0xfbde8e79,
    'CrouchStillSpread': 0x81fec758,
    'Damage': 0x59e94c40,
    'DamageAttachPoint': 0xca698181,
    'DamageDeduction': 0xaf922a6b,
    'DamageEffect': 0xae2bfdd1,
    'DamageEffectScale': 0x57ce6c85,
    'DamageInheritVelocity': 0xd06d0b7c,
    'DamageRadius': 0xb68798a6,
    'DamageRadiusInner': 0xded40df6,
    'DamageRadiusOuter': 0xa23b939d,
    'DamageStartPercent': 0x06182385,
    'DamageStopPercent': 0x37fe5ca9,
    'DamageThreshold': 0xcca74473,
    'DarknessMax': 0x25e5c3fc,
    'DarknessMin': 0x13fac25e,
    'DeathAnimation': 0x5fac58b5,
    'DeathAnimationExplosion': 0x07fe74d0,
    'DeathAnimationExplosionTime': 0x871eb169,
    'DeathDustDelay': 0xae640110,
    'DeathDustEffect': 0x7c8816fc,
    'DeathDustOffset': 0x060c07e2,
    'DeathEffect': 0xf138015c,
    'DeathEffectOffset': 0x29824727,
    'DeathOnCollision': 0x3fd818d0,
    'DeathShakeDelay': 0x0c13fc70,
    'DeathShakeDuration': 0xbb80d985,
    'DeathShakeForce': 0x94b9538c,
    'DeathShakeRadius': 0xb3af758b,
    'DeathSound': 0x6a9d502c,
    'DeathTime': 0xb4c6360c,
    'Decal': 0xde15f6ae,
    'DecayTime': 0x1c098b3c,
    'Deceleration': 0x8b12c806,
    'DeflectSound': 0xc20dfe6f,
    'DenyFlyerLand': 0x6d8fe606,
    'deploy': 0x5cd3477e,
    'DestroyedGeometryName': 0x5dc6e917,
    'DetatchSound': 0x5ede4703,
    'DisableForCloneWars': 0x6b014234,
    'DisableTime': 0x1c1694fa,
    'Discharge': 0x8b83f9b7,
    'DischargeSound': 0x16e4a90e,
    'DisguiseOwnerModel': 0x4e3c2ed2,
    'DisputeSound': 0x12caacaa,
    'DroidHealth': 0x9622c73b,
    'DroidScale': 0x338a07cd,
    'DropItemClass': 0x406d2b75,
    'DropItemProbability': 0x26996dae,
    'DropShadowSize': 0x82af5399,
    'Effect': 0x6e6e8d54,
    'EffectRegion': 0xa4f267b8,
    'eject': 0xdedc67f6,
    'Emitter': 0x576b09cd,
    'EnableDeathExplosions': 0x3e4e9ba0,
    'EnemyColor': 0x82e6120a,
    'EngineSound': 0x84bbef6a,
    'ExpireEffect': 0x028b22cf,
    'ExpireTimeEnemy': 0x98fcc969,
    'ExpireTimeField': 0x937e6a7d,
    'Explosion': 0x02bb1fe0,
    'ExplosionClass': 0xca0c1378,
    'ExplosionCritical': 0xe04f08c1,
    'ExplosionDeath': 0xa2723442,
    'ExplosionDestruct': 0x8a323f32,
    'ExplosionExpire': 0x2e51081f,
    'ExplosionImpact': 0x61a8bb12,
    'ExplosionName': 0x9b30e763,
    'ExplosionOffset': 0xc5637083,
    'ExplosionTrigger': 0x6a5e371c,
    'ExtremeRange': 0x8474ea2c,
    'EyePointCenter': 0x2d1420e5,
    'EyePointOffset': 0x41568c97,
    'FadeOutTime': 0x798dc484,
    'FinalExplosion': 0x58e1ba4e,
    'FinalExplosionOffset': 0xa47728f9,
    'FinAnimation': 0xef563a98,
    'FireAnim': 0x5c0246c4,
    'FireEmptySound': 0x20e1e379,
    'FireLoopSound': 0xb53b908e,
    'FireNodeName': 0x2e5375da,
    'FireOutsideLimits': 0x444f8958,
    'FirePoint': 0x0df83e75,
    'FirePointName': 0x4274fc96,
    'FireSound': 0xcfde2fc0,
    'FireSoundStop': 0x22624b58,
    'FireStateTime': 0x24157a9b,
    'FireVelocity': 0xf4d868ee,
    'FirstPerson': 0x6363d774,
    'FirstPersonFOV': 0x4785d6b7,
    'FirstRadius': 0x9cc82b1f,
    'FlareAngle': 0x5ae03a9e,
    'FlareIntensity': 0x633ed9d4,
    'FlashColor': 0xeb4230ac,
    'FlashLength': 0xb7b2d011,
    'FlashLightColor': 0xf2e54d72,
    'FlashLightDuration': 0xa3bfd787,
    'FlashLightRadius': 0x83eea041,
    'FlatCount': 0x4b6d5171,
    'FlatFaceFactor': 0xf6582b9c,
    'FlatGrassSwing': 0x604db82e,
    'FlatHeight': 0x231fcc79,
    'FlatSizeMultiplier': 0xa9b14958,
    'FleeSound': 0x94353bf8,
    'FlickerPeriod': 0xd92ea25e,
    'FlickerType': 0x3685bb77,
    'FlyerBan': 0x1cd984f6,
    'FLYERSECTION': 0x4cbe283c,
    'FoleyFXClass': 0x99d55922,
    'FoleyFXGroup': 0xa1c9cbc5,
    'FootBoneLeft': 0xd382edb2,
    'FootBoneRight': 0xa2f4825f,
    'Footstep0Sound': 0x21f56ed0,
    'Footstep1Sound': 0x937ceaa5,
    'Footstep2Sound': 0x12b23362,
    'FootstepSound0': 0x97157af6,
    'FootstepSound1': 0x98157c89,
    'FootStepSound1': 0x98157c89,
    'FootstepSound2': 0x951577d0,
    'FootStepSound2': 0x951577d0,
    'FootstepSound3': 0x96157963,
    'FootstepSound4': 0x9b158142,
    'FootstepSound5': 0x9c1582d5,
    'FootWaterSplashEffect': 0x057266ee,
    'ForceFireAnimation': 0x079c1d86,
    'ForceMode': 0x9d1f5707,
    'ForwardSpeed': 0xd42834bd,
    'ForwardTurnSpeed': 0x7eab3c84,
    'Friction': 0xa51be2bb,
    'FriendlyColor': 0x68daede1,
    'frontal_target': 0x822d162f,
    'FXName': 0xb5234678,
    'GeometryAddon': 0x94272331,
    'GeometryColorMax': 0x35b1cfc2,
    'GeometryColorMin': 0x3f9cc4c8,
    'GeometryLowRes': 0xa490eba1,
    'geometryNameGeometryName': 0xadaca80d,
    'geometryScaleGeometryScale': 0x5a0173c5,
    'GlowLength': 0xc3a8b510,
    'Gravity': 0xd209ff45,
    'GravityScale': 0x97f2e0f1,
    'GroundedHeight': 0x3a3614a0,
    'GroundedSound': 0x14d902a6,
    'HealthScale': 0xc37970cf,
    'HealthSScale': 0xf7cf8c2e,
    'HealthStatusTexture': 0x50938be8,
    'HealthTexture': 0x0db7468e,
    'Healthtype': 0xe8821677,
    'HealthType': 0xe8821677,
    'HeardEnemySound': 0xd3c54780,
    'HeatPerShot': 0x67cffd1a,
    'HeatRecoverRate': 0x57e7bba3,
    'HeatThreshold': 0x5621511e,
    'Height': 0xd5bdbb42,
    'HeightScale': 0xcaaa3778,
    'HideHealthBar': 0xe921a7d8,
    'HideOnFire': 0x5578d44c,
    'HideUnbuiltModel': 0x0d689977,
    'HidingSound': 0xc007b675,
    'HierarchyLevel': 0x407e801e,
    'HighResGeometry': 0x8b3185dd,
    'HitLocation': 0xced77479,
    'HitSound': 0xc5bdd741,
    'HoloBeamIntensity': 0xf31c745f,
    'HoloFadeInTime': 0x9fe971e5,
    'HoloFlareIntensity': 0x4cecac28,
    'HoloFlickerAlphaMax': 0x8710d279,
    'HoloFlickerAlphaMin': 0x78fd34b7,
    'HoloFlickerRate': 0xa0f13d29,
    'HoloHeight': 0xb761134e,
    'HoloImageGeometry': 0xb64210d2,
    'HoloImageIntensity': 0x543722af,
    'HoloLightIntensity': 0xf0ac6de0,
    'HoloLightRadius': 0x1d7b0711,
    'HoloOdf': 0x6a83ed9c,
    'HoloPopRate': 0x186a4586,
    'HoloRotateRate': 0xaff1f98c,
    'HoloSize': 0x3d60bcc8,
    'HoloTurnOnTime': 0x630c0e9e,
    'HoloType': 0x02565bd1,
    'HoloVisibleDistance': 0x09f126c2,
    'HorizontalSpread': 0x26b090c2,
    'HoverBan': 0x58fc17ee,
    'HugeBan': 0xb08090e7,
    'HurtSound': 0x72981af7,
    'HydraulicLowerHeight': 0x08080fd4,
    'HydraulicLowerSound': 0x0379fd4a,
    'HydraulicSound': 0x069134e5,
    'HydraulicSoundHeight': 0x8ae91462,
    'IconStatusTexture': 0x935558c5,
    'IconTexture': 0x8ddbeb4b,
    'IdleAnimation': 0x297bc6eb,
    'IdleDelay': 0xff701082,
    'IdleRotateSpeed': 0xede68c8b,
    'IdleWaitTime': 0x044894ab,
    'IdleWobbleFactor': 0x19e0afd9,
    'IdleWobbleLeftFoot': 0x1c1b9c83,
    'IdleWobbleNode': 0x1b5b62ea,
    'IdleWobbleRightFoot': 0x6eefb998,
    'IgnorableCollsion': 0x4aee3e6b,
    'ImpactEffect': 0x11727a92,
    'ImpactEffectRigid': 0xa3091269,
    'ImpactEffectShield': 0x4bc6c22f,
    'ImpactEffectSoft': 0xd6220fe6,
    'ImpactEffectStatic': 0x087ea2f0,
    'ImpactEffectTerrain': 0x5a554273,
    'ImpactEffectWater': 0xecaaa59d,
    'ImpMusic': 0xcedc7e88,
    'InitialCableLength': 0xe4c659b4,
    'InitialSalvoDelay': 0xc8388d9d,
    'InputSystem': 0xc21867e2,
    'InstanceProperties': 0x7c4ab7df,
    'IsPilotExposed': 0x2b60e217,
    'JetDuration': 0x10e3903c,
    'JetEffect': 0x69c4d0dd,
    'JetFuelCost': 0x36d9de4d,
    'JetFuelInitialCost': 0x1ebb5841,
    'JetFuelMinBorder': 0xf8a37c8a,
    'JetFuelRechargeRate': 0x0825c1bf,
    'JetJump': 0xc4b2cb20,
    'JetPush': 0xf0b75e90,
    'JetType': 0x91fabb5c,
    'jump': 0xa73f5c0d,
    'JumpDeduction': 0xfc0d5e74,
    'JumpSound': 0x580dc4ec,
    'KickBuildup': 0x069ad4d0,
    'KickSpread': 0xef4935b0,
    'KickStrength': 0x16e4db4a,
    'KillRegion': 0x76ed2f81,
    'KillSoldierSound': 0xf949d898,
    'Label': 0xf69717fd,
    'LandedHeight': 0x7642977a,
    'LandingSpeed': 0x6ae3a957,
    'LandingTime': 0x1283209d,
    'LandSound': 0xad3e89e3,
    'LaserGlowColor': 0x30580110,
    'LaserLength': 0xba858240,
    'LaserTexture': 0xb709b5e7,
    'LaserWidth': 0x6f179ab8,
    'LeftFootstepSound': 0xf3e10235,
    'LegBoneLeft': 0x03fd0638,
    'LegBoneRight': 0xc42be48d,
    'LegBoneTopLeft': 0x580f4d75,
    'LegBoneTopRight': 0x9eb9fc8e,
    'LegPairCount': 0x153289ae,
    'LegRayHitLength': 0x391bbcda,
    'LevelDamp': 0x252dfaab,
    'LevelFilter': 0xf4f5f38f,
    'LevelSpring': 0x02e46404,
    'Lifespan': 0x7c7c544b,
    'LifeSpan': 0x7c7c544b,
    'LiftDamp': 0xa37b2ec6,
    'LiftSpring': 0x1b5071f9,
    'LightColor': 0x746ce73e,
    'LightDuration': 0x6370a66b,
    'Lighting': 0x827eb1c9,
    'LightningEffect': 0x6dd5a894,
    'LightRadius': 0x2776564d,
    'lights': 0x1956cad4,
    'LocalsColor': 0x9eb4d884,
    'LockedOnSound': 0x9371aecd,
    'LockedSound': 0x027b5cb2,
    'LockOffAngle': 0xc915b156,
    'lockOnAngleLockOnAngle': 0x763b6223,
    'LockOnRange': 0x7f012f70,
    'LockOnTime': 0x5f7bc3b2,
    'LockTime': 0x448fbce3,
    'LostSound': 0x8e39006a,
    'LowHealthSound': 0xf8d3e5d2,
    'LowHealthThreshold': 0xc865523e,
    'LowResModel': 0x0df468ca,
    'MapScale': 0x0e8c3fe5,
    'MapTexture': 0x9dc38d80,
    'MaxAlpha': 0xb1e439af,
    'MaxBallAngle': 0xe6f7befb,
    'MaxChargeStrengthHeavy': 0xa61d280f,
    'MaxChargeStrengthLight': 0xe6c12d74,
    'MaxDamage': 0x47d0e794,
    'MaxDelayHeavy': 0x7189dcc3,
    'MaxDelayLight': 0xe2742820,
    'MaxDistance': 0xe6915cf6,
    'MaxFallingLeaves': 0xfd7fae90,
    'MaxHealth': 0x19971f1b,
    'MaxHeavy': 0x25779a5c,
    'MaxHeavyDecay': 0xf440c23a,
    'MaxInterval': 0x8b37cab4,
    'MaxItems': 0x54c3c993,
    'MaxJumpDistance': 0xad37744e,
    'MaxLifetime': 0x9d399b92,
    'MaxLifeTime': 0x9d399b92,
    'MaxLight': 0x569c3e43,
    'MaxLightDecay': 0x78221603,
    'MaxPitchSpeed': 0xb5534be0,
    'MaxPos': 0x38b0b50d,
    'MaxPressedTime': 0x2819ffa0,
    'MaxPush': 0xaee05d99,
    'MaxRange': 0x43bcebe6,
    'MaxScatterBirds': 0x3b1948f3,
    'MaxShakeAmt': 0xc3e9c081,
    'MaxShakeLen': 0x626eeba0,
    'MaxShield': 0xda3491bc,
    'MaxSize': 0x80ba1308,
    'MaxSkew': 0x97133eeb,
    'MaxSpeed': 0x86df0364,
    'MaxSpread': 0xaedcbd12,
    'MaxStrafeSpeed': 0x3437a33d,
    'MaxStrength': 0x40bd9b1c,
    'MaxTargets': 0xa00a48cd,
    'MaxTerrainAngle': 0x47a95951,
    'MaxTimeLeftHeavy': 0x220abe04,
    'MaxTimeLeftLight': 0x931a6a3b,
    'MaxTurnSpeed': 0x5433f589,
    'MaxVel': 0xa7bcb86c,
    'MaxYawSpeed': 0x7335aa87,
    'MediumBan': 0xc8f3c76b,
    'MidSpeed': 0x838bda20,
    'MinAlpha': 0x7db59929,
    'MinDamage': 0xfe544f96,
    'MinDelayHeavy': 0x1cb9e68d,
    'MinDelayLight': 0xe1c681ca,
    'MinDistance': 0xb835cf50,
    'MinEnemyRadius': 0x479e5b63,
    'MinHeavy': 0x4456e84a,
    'MinHeavyDecay': 0xa4fbdbc8,
    'MinInterval': 0xf8c69a26,
    'MinLifetime': 0xbd9397ec,
    'MinLifeTime': 0xbd9397ec,
    'MinLight': 0x5a4042b1,
    'MinLightDecay': 0x1c5461b1,
    'MinPos': 0x597c1bb7,
    'MinPush': 0x3ed11ac3,
    'MinRange': 0x1ef25b6c,
    'MinShakeAmt': 0x4fb4269f,
    'MinShakeLen': 0xcff18812,
    'MinSize': 0xeaebcf6e,
    'MinSpeed': 0xfbe2eb62,
    'MinSpread': 0x59053068,
    'MinStrength': 0x4d832102,
    'MinTimeLeftHeavy': 0xbf6413ae,
    'MinTimeLeftLight': 0x4104158d,
    'MinVel': 0xb10f20ca,
    'ModeTexture': 0x54e9f4e5,
    'ModeTextureColor': 0xef3e81f8,
    'MountPos': 0xf2aa4a90,
    'MoveTension': 0x21050bf6,
    'MoveTensionX': 0x88f1308a,
    'MoveTensionY': 0x89f1321d,
    'MoveTensionZ': 0x86f12d64,
    'MovingTurnOnly': 0x3c45420e,
    'Music': 0x9f9c4fd4,
    'MusicDelay': 0x1784e0a3,
    'MusicSpeed': 0x4defb65f,
    'MuzzleFlash': 0xcfcccbce,
    'MuzzleFlashEffect': 0x39aaa863,
    'NeutralColor': 0xb135436f,
    'NeutralizeTime': 0xf1a8f31b,
    'NextAimer': 0x665d96ea,
    'NextBarrel': 0xe98f377c,
    'NextChargeNEXTCHARGE': 0x42541d39,
    'NextDropItem': 0x5ea04066,
    'NoCombatInterrupt': 0x28adda49,
    'NoDeathExplosions': 0x16181b74,
    'NoEnterVehicles': 0x939b9985,
    'NoRandomSpring': 0x7a5de0fc,
    'NormalDirection': 0xde649a87,
    'NumChunks': 0xf54f2869,
    'NumDustObjectsInEffects': 0x458975f0,
    'NumParticles': 0xd133f7da,
    'NumParts': 0x5ac02207,
    'NumRays': 0xf357466a,
    'NumVisible': 0x1abd7877,
    'Odf': 0xab409a38,
    'Offset': 0x14c8d3ca,
    'OmegaXDamp': 0x9d59000a,
    'OmegaXSpring': 0x9184393d,
    'OmegaZDamp': 0xaa764468,
    'OmegaZSpring': 0x37949663,
    'OmniLightRadius': 0xa0fff23e,
    'OmniRadius': 0xc2c1813a,
    'OpenSound': 0x323f7450,
    'OptimalRange': 0x778f9aae,
    'OrdnanceClass': 0xd59a9357,
    'Ordnancecollision': 0xfb2bdf07,
    'OrdnanceCollision': 0xfb2bdf07,
    'OrdnanceCollisionPrim': 0x330acaab,
    'OrdnanceEffect': 0x3f30370c,
    'OrdnanceGeometryName': 0xa6032172,
    'OrdnanceName': 0xf8899c5e,
    'OrdnanceSound': 0xccf9be5c,
    'OverheatSound': 0xf4a517d4,
    'OverheatSoundPitch': 0xb52f4e1a,
    'OverheatStopSound': 0xa0b09f74,
    'OverrideTexture': 0x09db74ac,
    'OverrideTexture2': 0x227894ba,
    'PCaxPitchSpeed': 0x3defee6c,
    'PCMaxPitchSpeed': 0x48e46a1b,
    'PCMaxStrafeSpeed': 0x4bbfdeec,
    'PCMaxTurnSpeed': 0x276faf5c,
    'PCMaxYawSpeed': 0x934d56e0,
    'PCPitchRate': 0x841bfeb8,
    'PCPitchSpeed': 0x2b92518d,
    'PCPitchTurnFactor': 0x8624d352,
    'PCSpinRate': 0x7c21a3b6,
    'PCTurnRate': 0x3c11e4c1,
    'PCTurnSpeed': 0xc99b10e6,
    'PCYawTurnFactor': 0x0e8662f7,
    'PersonHealth': 0xf51ad206,
    'PersonScale': 0x0bb94602,
    'Pilot9Pose': 0xa976d065,
    'PilotAnimation': 0x6e4fc069,
    'PilotPosition': 0x51ca39a6,
    'PilotSkillRepairScale': 0x0842b6a7,
    'PilotType': 0x91ee6929,
    'pitch_down': 0x0e0b93a2,
    'pitch_up': 0x3f02fd67,
    'pitch': 0xbd324ab1,
    'PitchDamp': 0xfeaba02f,
    'PitchFilter': 0x9b0ca8c3,
    'PitchLimits': 0x3403b139,
    'PitchRate': 0xb9b8abc3,
    'PitchSpread': 0x8d0cb6ca,
    'PitchTurnFactor': 0x0b2fc2f9,
    'PowerupDelay': 0x299acaba,
    'Powerupsound': 0xa2a034ea,
    'PPitchRate': 0xfa5d55a1,
    'PreparingForDamageSound': 0x130971ae,
    'PrimaryWeapon': 0xdc697015,
    'ProneMoveSpread': 0x73608c73,
    'ProneSound': 0xcadb9d74,
    'ProneStillSpread': 0x4a29a3ca,
    'Push': 0x876fffdd,
    'PushDeduction': 0x58a7da24,
    'PushRadius': 0x19b5e2bb,
    'PushRadiusInner': 0x96301ec5,
    'PushRadiusOuter': 0x71262ebe,
    'Radius': 0x0dba4cb3,
    'RadiusFadeMax': 0x6e74d661,
    'RadiusFadeMin': 0x80887a6f,
    'Range': 0xfadc0cd2,
    'RayRadius': 0xa4c53efd,
    'RayTriggerMinSpeed': 0xdc6a93e6,
    'RayTriggerWidth': 0x42e950ab,
    'Rebound': 0x678de338,
    'RecoilDecayHeavy': 0xb97f1f52,
    'RecoilDecayLight': 0xa9b93c09,
    'RecoilDelayHeavy': 0xb7c581ad,
    'RecoilDelayLight': 0x7cd21cea,
    'RecoilLengthHeavy': 0x4b92a06a,
    'RecoilLengthLight': 0x903574d1,
    'RecoilStrengthHeavy': 0x12ba9f01,
    'RecoilStrengthLight': 0xcf3649e6,
    'RefillFromItem': 0xc7af6c62,
    'ReloadSound': 0xef6119f3,
    'ReloadTime': 0x9fc1a1ad,
    'RepMusic': 0x9347d123,
    'ReserveOneForPlayer': 0xadf73cb1,
    'ResetTeam': 0x2e4c2b79,
    'RespawnTime': 0xbd94b44e,
    'RestDir': 0xb6ebf796,
    'ReticuleTexture': 0x617e2f93,
    'ReverseSpeed': 0x1f069ec0,
    'RightFootstepSound': 0x58a1f462,
    'RollSound': 0xd211149d,
    'Rotation': 0x21ac415f,
    'RotationRate': 0xe6989765,
    'RotationVelocity': 0x164b5138,
    'RoundDelay': 0x2616233a,
    'RoundsPerClip': 0x7bff9ec9,
    'RoundsPersalvo': 0x168ad1d6,
    'RoundsPerSalvo': 0x168ad1d6,
    'SalvoCount': 0x9260ea63,
    'SalvoDelay': 0xd76f37db,
    'SalvoTime': 0x4225631d,
    'ScanningRange': 0x465909fb,
    'ScatterDistance': 0xebd81a5e,
    'SCDriverGetInSound': 0x47041baf,
    'SCDriverGetOutSound': 0x4efe8d94,
    'SCFieldFollowSound': 0x491b3917,
    'SCFieldHoldSound': 0xb2a1a19f,
    'SCFieldMoveOutSound': 0xe0e7aa4f,
    'SCGunnerAllClearSound': 0xa3d45943,
    'SCGunnerGetInSound': 0xd1f9b472,
    'SCGunnerGetOutSound': 0xc27c316f,
    'SCGunnerSteadySound': 0x981f3d5d,
    'ScopeTexture': 0x32e2a37a,
    'SCPassengerGetInSound': 0x6c89065f,
    'SCPassengerGetOutSound': 0xf260f2a4,
    'SCPassengerMoveOutSound': 0x5b7c85cb,
    'SCPassengerStopSound': 0x5d42f4c8,
    'SCResponseNosirSound': 0xc989ade6,
    'SCResponseYessirSound': 0x765be0f2,
    'SecondaryWeapon': 0x4adc9acd,
    'Seed': 0x5045bcac,
    'SelfDestructSoundPitch': 0x4c5aa5aa,
    'SetAltitude': 0x4f358485,
    'Shake': 0xbd8bb2f5,
    'ShakeLength': 0x25b787e5,
    'ShakeRadius': 0xd634b283,
    'ShakeRadiusInner': 0x4954490d,
    'ShakeRadiusOuter': 0x125399a6,
    'ShieldEffect': 0xddb924a1,
    'ShieldOffset': 0x1d726313,
    'ShieldOffSound': 0x5df6c1a4,
    'ShieldRadius': 0x5a9201b6,
    'ShieldScale': 0xd0545c72,
    'ShieldSound': 0xd85503ff,
    'ShockFadeInTime': 0x716adadd,
    'ShockFadeOutGain': 0xecf4a152,
    'ShockFadeOutTime': 0x20cd1d00,
    'ShockSound': 0xf66784c8,
    'shotdelayShotDelay': 0x825edb67,
    'ShotElevate': 0xae3db60d,
    'ShotPatternCount': 0xa4dfafc0,
    'ShotPatternPitchYaw': 0xa4120aa8,
    'ShotsPerSalvo': 0x03b38558,
    'SkeletonLowRes': 0x55f297d2,
    'SkeletonLowResRootScale': 0xc97df4a4,
    'SkeletonName': 0x7012f6cd,
    'SkeletonRootScale': 0x4cacc3d0,
    'SkeletonRootScaleLowRes': 0x26239cd4,
    'SkinnyFactor': 0xff7bb39a,
    'SmallBan': 0x6d1ca06d,
    'SmashParkedFlyers': 0x7fdeedf1,
    'SniperScope': 0xf15aaeb2,
    'SoldierAmmo': 0xc3da529f,
    'SoldierAnimation': 0x5f0ce10d,
    'SoldierBan': 0x3994a056,
    'soldierCollisionSoldiercollision': 0xebdda3d9,
    'SoldierCollision': 0x5dfdc07f,
    'SoldierCollisionOnly': 0x605a7141,
    'SoldierCollisionPrim': 0x07d00083,
    'SoldierHealth': 0xf33b41df,
    'Sound': 0x0e0d9594,
    'SoundName': 0x7a5ff18f,
    'SoundPitchDev': 0xa33d3401,
    'SoundProperty': 0xf350b4e5,
    'SpawnPath': 0xdde0b14f,
    'SpawnPointCount': 0x32579f4d,
    'SpawnPointLocation': 0xa067d145,
    'SpawnSound': 0xb4368857,
    'SpawnTime': 0x4e99b371,
    'SpinRate': 0xddd0e74b,
    'SpreadLimit': 0x85a6b6fd,
    'SpreadPerShot': 0x43ab2c7d,
    'SpreadRadius': 0x82a0379c,
    'SpreadRecover': 0x33841a8a,
    'SpreadRecoverRate': 0xccedb638,
    'SpreadThreshold': 0x2613b9b9,
    'SquatSound': 0xfc9b0358,
    'StandMoveSpread': 0xf7561531,
    'StandSound': 0x0e8b2d62,
    'StandStillSpread': 0x4c081d30,
    'staticStatic': 0xe2db8cd1,
    'StatusTexture': 0x037cd46e,
    'steer_left': 0xd40a58f2,
    'steer_right': 0x6462329f,
    'steer': 0x1301ae76,
    'StickAnimal': 0xd1b49b73,
    'StickBuilding': 0x7449c0b3,
    'StickBuildingDead': 0xad9c5fa5,
    'StickBuildingUnbuilt': 0xa8a2aff4,
    'StickDroid': 0x3b3f45b7,
    'StickPerson': 0x01e9caea,
    'StickTerrain': 0x95706d30,
    'StickVehicle': 0x9b4af9ed,
    'StompDecal': 0x9b650367,
    'StompDecalSize': 0xe611ed7e,
    'StompDetectionType': 0xb32208ed,
    'StompEffect': 0x07ff5a07,
    'StompThreshold': 0x4f08e1f5,
    'StoppedTurnSpeed': 0x7c8f02c0,
    'strafe_left': 0xdfe8689a,
    'strafe_right': 0x9920b8e7,
    'strafe': 0xd29ed7ce,
    'StrafeRollAngle': 0xf1a4896c,
    'StrafeSpeed': 0xfe1ce511,
    'Strategic_Filter1': 0xccb0b36b,
    'Strategic_Filter2': 0xcdb0b4fe,
    'Strategic_Filter3': 0xceb0b691,
    'Strategic_Filter4': 0xcfb0b824,
    'Strategic_Filter5': 0xd0b0b9b7,
    'Strategic_Filter6': 0xd1b0bb4a,
    'StrikeOrdnanceName': 0x6fd92be8,
    'SuppressRadius': 0xce754894,
    'SuspensionLeftArmNodeName': 0xabb24116,
    'SuspensionMaxOffset': 0xf0856c5d,
    'SuspensionMidOffset': 0x8eda7a09,
    'SuspensionNodeName': 0xe534c2cb,
    'SuspensionRightArmNodeName': 0x580b459f,
    'SwingSpeed': 0x862be6b4,
    'SwingTime': 0x7c9c8ae0,
    'SwitchImmediately': 0xc43b77dd,
    'TakeoffHeight': 0x5107fafc,
    'TakeoffSound': 0xc093b232,
    'TakeoffSpeed': 0x8255424e,
    'TakeoffTime': 0x61195c0a,
    'TargetableCollision': 0xd23dbaf8,
    'TargetAnimal': 0x75c58748,
    'TargetBuilding': 0xc4409ff0,
    'TargetDroid': 0x19007f1a,
    'TargetEnemy': 0xe10d2224,
    'TargetFriendly': 0xca7f5887,
    'TargetNeutral': 0x5f0ae167,
    'TargetPerson': 0xfae6054d,
    'TargetVehicle': 0x281b9338,
    'TEMP_AnimationSpeed': 0x6b8d8679,
    'TEMP_Type': 0x96b6fd80,
    'TerrainCollision': 0xafe693ce,
    'TerrainCollisionPrim': 0x7cdccf2a,
    'TerrainLeft': 0x21322adb,
    'TerrainRight': 0xb62deb24,
    'Texture': 0x3c6468f4,
    'ThirdPersonFOV': 0x20728c12,
    'throttle_down': 0xf9a91e2e,
    'throttle_up': 0xbff5ea7b,
    'throttle': 0x378f32dd,
    'ThrustAttachOffset': 0x34775769,
    'ThrustAttachPoint': 0x2e0557f0,
    'ThrustEffect': 0x0894d756,
    'ThrustEffectMaxScale': 0xc3fd784a,
    'ThrustEffectMinScale': 0xf174a3f8,
    'ThrustEffectScaleStart': 0xe97041b8,
    'ThrustPitchAngle': 0x4c5b08a6,
    'TickSound': 0xacfe0d9b,
    'TickSoundPitch': 0x18953967,
    'TiltValue': 0x359d5227,
    'TowCableCollision': 0x2436d722,
    'track_pitch_minus': 0xd9e5ee0a,
    'track_pitch_plus': 0xd6c74252,
    'track_pitch_reset': 0xe8964c81,
    'track_yaw_minus': 0x200442c3,
    'track_yaw_plus': 0x19065b49,
    'track_yaw_reset': 0x5384cc04,
    'TrackCenter': 0xe85d5895,
    'TrackDeathOnAttach': 0x0550a3b2,
    'TrackingSound': 0xe8345a43,
    'TrackOffset': 0xfd3d9507,
    'Traction': 0x4fe8d3f1,
    'TrailEffect': 0x7e71e2c6,
    'TrakCenter': 0x1081c71a,
    'TransmitRange': 0xeb460a76,
    'TransparentType': 0x9c3f7a19,
    'TrialEffect': 0x69fdf6f6,
    'TriggerAll': 0x1c1b6976,
    'TriggerAnimation': 0xf7a5d75b,
    'TriggerCollision': 0x146ffe85,
    'TriggerContact': 0xbfb22e35,
    'TriggerOffset': 0xfe7c5230,
    'TriggerRadius': 0xc461d811,
    'TriggerSingle': 0xed9d56db,
    'TriggerTeam': 0xabcb950a,
    'TurnFilter': 0xde721cb4,
    'TurningOffSound': 0x7d2c2fa2,
    'TurnOffSound': 0x042dabae,
    'TurnOffTime': 0xc8a9e3c6,
    'TurnOnSound': 0xea603e52,
    'TurnOnTime': 0x08aab3aa,
    'TurnRate': 0x0f77c4e8,
    'TurnThreshold': 0x46bba6d5,
    'TurretActivateSound': 0xe9d0fb69,
    'TurretAmbientSound': 0x8e5da6e8,
    'TurretDeactivateSound': 0xf84aa204,
    'TurretMoveSound': 0x4c39154d,
    'TurretMoveSoundStartEndPitch': 0x9e4f2daa,
    'TurretMoveSoundStartEndTime': 0x5fdfe105,
    'TurretNodeName': 0xb69a7cb4,
    'TurretPitchSound': 0x28f016d2,
    'TurretPitchSoundPitch': 0x4ed7a4d0,
    'TURRETSECTION': 0xad7915d2,
    'TurretStartSound': 0x8822cb3c,
    'TurretStopSound': 0xc13068b6,
    'TurretYawSound': 0x1fa43b99,
    'TurretYawSoundPitch': 0x1503f425,
    'UnbuiltGeometryName': 0x97c931c5,
    'UnbuiltHoloOdf': 0x48542041,
    'unitName': 0x45a8bc04,
    'UnitType': 0x54a7aedf,
    'UprightLowResModel': 0xf1f9f3e3,
    'UprightWaterDamageHeight': 0xf01d5583,
    'UseVCollForFlyers': 0xf31d1478,
    'Value_ATK_Alliance': 0xa340d6b5,
    'Value_ATK_CIS': 0x00e73245,
    'Value_ATK_Empire': 0x4db44670,
    'Value_ATK_Locals': 0x573c98a4,
    'Value_ATK_Republic': 0x9e78b410,
    'Value_DEF_Alliance': 0x44a2c4a6,
    'Value_DEF_CIS': 0x5bf85ae8,
    'Value_DEF_Empire': 0xa8679457,
    'Value_DEF_Locals': 0xe689ef93,
    'Value_DEF_Republic': 0x8f5540cb,
    'ValueBleed': 0x4ebf97da,
    'VehicleAmmo': 0xe728d955,
    'vehiclecollision': 0xde5365a1,
    'Vehiclecollision': 0xde5365a1,
    'VehicleCollision': 0xde5365a1,
    'vehiclecollisiononly': 0xc3f25cbb,
    'VehicleCollisiononly': 0xc3f25cbb,
    'VehicleCollisionOnly': 0xc3f25cbb,
    'VehicleCollisionPrim': 0xfec8cea9,
    'VehicleCollisionSound': 0x84824518,
    'VehicleHealth': 0x14e381c9,
    'VehiclePosition': 0xda1b8c0c,
    'VehicleScale': 0x6ccdc5ef,
    'VehicleType': 0x5233b817,
    'Velocity': 0x32741c32,
    'VelocityDamp': 0x661d8524,
    'VelocitySpring': 0xdf0d2c6f,
    'VerticalSpread': 0xb0d0544c,
    'Vine': 0xcdbc383d,
    'Virtual': 0x5d967ebc,
    'VO_All_AllCapture': 0x13ad1ea0,
    'VO_All_AllInDispute': 0x22bd3453,
    'VO_All_AllInfo': 0xba31cb0a,
    'VO_All_AllLost': 0x9e71f320,
    'VO_All_AllSaved': 0xfd4b3aa1,
    'VO_All_ImpCapture': 0x64340317,
    'VO_All_ImpInDispute': 0xe018b5a4,
    'VO_All_ImpInfo': 0xf7c6eccb,
    'VO_All_ImpLost': 0xc0fc4645,
    'VO_All_ImpSaved': 0x1addabea,
    'VO_CIS_CISCapture': 0x8f270798,
    'VO_CIS_CISInDispute': 0x5ba686bb,
    'VO_CIS_CISInfo': 0xb708ce82,
    'VO_CIS_CISLost': 0xd4d671e8,
    'VO_CIS_CISSaved': 0x3ee46599,
    'VO_CIS_RepCapture': 0x1934685e,
    'VO_CIS_RepInDispute': 0x0d03a541,
    'VO_CIS_RepInfo': 0x66a3fa90,
    'VO_CIS_RepLost': 0x9f6648da,
    'VO_CIS_RepSaved': 0x6eb55ff7,
    'VO_Imp_AllCapture': 0xd74a7fcb,
    'VO_Imp_AllInDispute': 0x87834218,
    'VO_Imp_AllInfo': 0x05f2bec7,
    'VO_Imp_AllLost': 0x2446d141,
    'VO_Imp_AllSaved': 0x23121dde,
    'VO_Imp_ImpCapture': 0xbd2190b4,
    'VO_Imp_ImpInDispute': 0xded807e7,
    'VO_Imp_ImpInfo': 0x6f900a76,
    'VO_Imp_ImpLost': 0x1816200c,
    'VO_Imp_ImpSaved': 0xc2871425,
    'VO_Rep_CISCapture': 0x7b21958e,
    'VO_Rep_CISInDispute': 0x8653e871,
    'VO_Rep_CISInfo': 0x1f5e25a0,
    'VO_Rep_CISLost': 0xb2ba322a,
    'VO_Rep_CISSaved': 0x6d015027,
    'VO_Rep_RepCapture': 0x951d8f40,
    'VO_Rep_RepInDispute': 0xf8d18cf3,
    'VO_Rep_RepInfo': 0xbe2ad02a,
    'VO_Rep_RepLost': 0xa4e3ce40,
    'VO_Rep_RepSaved': 0x1bd37e41,
    'WakeEffect': 0x26d7a21c,
    'WakeWaterSplashEffect': 0xf44fee52,
    'WalkerLegPair': 0x2aea4add,
    'WalkerOrientRoll': 0x65587105,
    'WALKERSECTION': 0x1cd9f762,
    'WalkerWidth': 0x0b9bb9c9,
    'WaterDamageAmount': 0x829299ad,
    'WaterDamageInterval': 0x5b491acc,
    'WaterEffect': 0x87733801,
    'WaterSplashEffect': 0xdea64cfa,
    'WaterWadingSound': 0x6be6199f,
    'WaverRate': 0x6d4a8840,
    'WaverTurn': 0x129f08c1,
    'weapon_fire': 0xd06cf65e,
    'weapon_next': 0x2a88cdb7,
    'weapon_prev': 0x02c2085f,
    'weapon_special': 0xe9b16711,
    'WeaponAmmo': 0xdc19bd13,
    'WeaponAmmo1': 0x9e84bc86,
    'WeaponAmmo2': 0x9d84baf3,
    'WeaponAmmo3': 0x9c84b960,
    'WeaponAmmo4': 0xa384c465,
    'WeaponChange': 0x1ada38c1,
    'WeaponChangeSound': 0x352a4db8,
    'WeaponChannel': 0x16472328,
    'WeaponChannel1': 0x2afc405b,
    'WeaponChannel2': 0x2bfc41ee,
    'WeaponChannel3': 0x2cfc4381,
    'WeaponChannel4': 0x2dfc4514,
    'WeaponClass': 0xacda90ab,
    'WeaponName': 0xfbf47dba,
    'WeaponName1': 0x2ce1a1d1,
    'WeaponName2': 0x29e19d18,
    'WeaponName3': 0x2ae19eab,
    'WeaponName4': 0x2fe1a68a,
    'WeaponSection': 0xd0329e80,
    'WEAPONSECTION': 0xd0329e80,
    'WiggleAmount': 0x7cbb796c,
    'WiggleSpeed': 0xd4cbd35b,
    'WindSound': 0x96a1687e,
    'WingModel': 0x95437337,
    'YawLimits': 0x2c3e8078,
    'YawSpread': 0xebefdcd7,
    'YawTurnFactor': 0x0ebb87c8,
    'YOffset': 0x3d5d0aef,
    'zoom_factor_minus': 0x88d283ef,
    'zoom_factor_plus': 0xf6cd53b5,
    'zoom_factor_reset': 0xc72c0000,
    'ZoomFirstPerson': 0x14ec7e1d,
    'ZoomMax': 0x2a96e8b4,
    'ZoomMin': 0x1881b1a6,
    'ZoomRate': 0x9573fb20,
}

NAMES = []

for k in NAMES:
    print(f"'{k}': 0x{fnv1a_32(k):08x},")
