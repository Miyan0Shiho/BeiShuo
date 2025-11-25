// 碑文数据库
export const inscriptionsData = {
  // 首页精选碑文
  featuredInscriptions: [
    {
      id: "1988264127725830144",
      title: "李白墓碑文",
      description: "唐代著名诗人李白的墓碑，记载了诗仙的生平与文学成就",
      dynasty: "唐代",
      year: "公元766年",
      location: "当涂青山",
      image:
        "/gemdesign/assets/page/1988264127725830144/8c939d4ad1088f74dbcdbfb264c6e042.png",
      confidence: 98.7,
      category: "名人碑刻",
      views: 5420,
    },
    {
      id: "1988443551448432640",
      title: "王羲之兰亭集序碑",
      description: "天下第一行书《兰亭集序》的碑刻版本",
      dynasty: "东晋",
      year: "公元353年",
      location: "绍兴兰亭",
      image:
        "/gemdesign/assets/page/1988443551448432640/abd2b01b3b1666d55b0880e9c900db3b.png",
      confidence: 96.5,
      category: "书法碑刻",
      views: 8230,
    },
    {
      id: "1988557465465126912",
      title: "石鼓文碑",
      description: "我国现存最早的石刻文字之一，具有极高的文物价值",
      dynasty: "秦代",
      year: "公元前300年",
      location: "陕西凤翔",
      image:
        "/gemdesign/assets/page/1988557465465126912/f74b7a17cfb1aff9ccd278eb54e9769b.png",
      confidence: 95.2,
      category: "古代碑刻",
      views: 3150,
    },
    {
      id: "1988595444078346240",
      title: "多宝塔碑",
      description: "唐代颜真卿楷书代表作，记录多宝塔建造历史",
      dynasty: "唐代",
      year: "公元752年",
      location: "西安",
      image:
        "/gemdesign/assets/page/1988595444078346240/726b3c1ba023f2bb873d5877c88624fc.png",
      confidence: 97.8,
      category: "书法碑刻",
      views: 4560,
    },
    {
      id: "1988860433636786176",
      title: "泰山刻石",
      description: "秦始皇东巡泰山时所立的石刻，是研究秦代政治和文字的珍贵资料",
      dynasty: "秦代",
      year: "公元前219年",
      location: "山东泰山",
      image:
        "/gemdesign/assets/page/1988860433636786176/9d416c7b5536792579bf7a30ca9e59b9.png",
      confidence: 94.3,
      category: "历史碑刻",
      views: 6780,
    },
    {
      id: "1988876862763302912",
      title: "九成宫醴泉铭",
      description: "唐太宗时期欧阳询书写的楷书经典，记载了九成宫发现醴泉的故事",
      dynasty: "唐代",
      year: "公元632年",
      location: "陕西麟游",
      image:
        "/gemdesign/assets/page/1988876862763302912/ff3f38051fa0580ec4fa8bca4a825869.png",
      confidence: 98.1,
      category: "书法碑刻",
      views: 7240,
    },
    {
      id: "1990611432919531520",
      title: "张迁碑",
      description: "东汉隶书的代表作，记载了张迁的生平事迹",
      dynasty: "东汉",
      year: "公元186年",
      location: "山东东平",
      image:
        "/gemdesign/assets/page/1990611432919531520/d1192b167358d7db865b3fd76de247a4.png",
      confidence: 96.7,
      category: "书法碑刻",
      views: 4920,
    },
    {
      id: "1990617642804707328",
      title: "曹全碑",
      description: "东汉隶书名碑，书法秀美流畅，记载了曹全的生平",
      dynasty: "东汉",
      year: "公元185年",
      location: "陕西合阳",
      image:
        "/gemdesign/assets/page/1990617642804707328/cc16ad06f3e695c84272a5c5dc909381.png",
      confidence: 97.2,
      category: "书法碑刻",
      views: 5340,
    },
    {
      id: "1990655453893230592",
      title: "醉翁亭记碑",
      description: "宋代欧阳修所作《醉翁亭记》的碑刻版本，由苏轼手书",
      dynasty: "宋代",
      year: "公元1046年",
      location: "安徽滁州",
      image:
        "/gemdesign/assets/page/1990655453893230592/933799c1fd5f2ec1e910f7f82695329a.png",
      confidence: 98.5,
      category: "文学碑刻",
      views: 9120,
    },
  ],

  // 按朝代分类
  dynasties: [
    { id: "qin", name: "秦代", count: 5, color: "#8B5A2B" },
    { id: "han", name: "汉代", count: 12, color: "#D2691E" },
    { id: "wei-jin", name: "魏晋", count: 8, color: "#CD853F" },
    { id: "tang", name: "唐代", count: 25, color: "#DAA520" },
    { id: "song", name: "宋代", count: 18, color: "#B8860B" },
    { id: "yuan", name: "元代", count: 6, color: "#A0826D" },
    { id: "ming", name: "明代", count: 15, color: "#8B7355" },
    { id: "qing", name: "清代", count: 20, color: "#696969" },
  ],

  // 按类别分类
  categories: [
    {
      id: "famous-people",
      name: "名人碑刻",
      icon: "fas fa-user-tie",
      count: 45,
    },
    {
      id: "calligraphy",
      name: "书法碑刻",
      icon: "fas fa-pen-fancy",
      count: 38,
    },
    { id: "literature", name: "文学碑刻", icon: "fas fa-book", count: 22 },
    { id: "history", name: "历史碑刻", icon: "fas fa-landmark", count: 35 },
    { id: "ancient", name: "古代碑刻", icon: "fas fa-scroll", count: 28 },
    { id: "tomb", name: "墓志铭", icon: "fas fa-monument", count: 42 },
  ],

  // 热门标签
  popularTags: [
    "唐代书法",
    "秦始皇",
    "李白",
    "王羲之",
    "欧阳询",
    "颜真卿",
    "隶书",
    "楷书",
    "行书",
    "篆书",
    "历史人物",
    "文化遗产",
    "古代文学",
    "碑刻艺术",
  ],

  // 最新资讯
  news: [
    {
      id: 1,
      title: "新发现唐代石碑在西安出土",
      date: "2024-01-20",
      category: "考古发现",
      image:
        "/gemdesign/assets/page/1988264127725830144/05ef80e38e71b719a0cbbc374d31e3b4.png",
      excerpt:
        "考古队在西安市郊发现一块保存完好的唐代石碑，上面刻有珍贵的历史信息，为研究唐代文化提供了重要实物资料...",
      views: 1245,
      likes: 89,
    },
    {
      id: 2,
      title: "AI技术助力碑文保护与研究",
      date: "2024-01-18",
      category: "技术创新",
      image:
        "/gemdesign/assets/page/1988443551448432640/14d787832f08efe75f8cd90196bc39bb.png",
      excerpt:
        "最新AI识别技术在碑文保护领域取得突破，识别准确率提升至99%以上，极大地提高了碑文数字化保护效率...",
      views: 2130,
      likes: 156,
    },
    {
      id: 3,
      title: "全国碑文数字化项目启动",
      date: "2024-01-15",
      category: "行业动态",
      image:
        "/gemdesign/assets/page/1988557465465126912/1ea242ec247e0ed44498ddf06dd6489d.png",
      excerpt:
        "国家文物局启动全国重点碑文数字化保护项目，计划三年内完成万件碑文数字化，建立国家碑文数据库...",
      views: 985,
      likes: 72,
    },
  ],

  // 获取碑文详情
  getInscriptionById(id) {
    return this.featuredInscriptions.find((item) => item.id === id);
  },

  // 按朝代筛选
  filterByDynasty(dynastyId) {
    const dynasty = this.dynasties.find((d) => d.id === dynastyId);
    if (!dynasty) return [];
    return this.featuredInscriptions.filter((item) =>
      item.dynasty.includes(dynasty.name.replace("代", ""))
    );
  },

  // 按类别筛选
  filterByCategory(categoryId) {
    const category = this.categories.find((c) => c.id === categoryId);
    if (!category) return [];
    return this.featuredInscriptions.filter(
      (item) => item.category === category.name
    );
  },

  // 搜索碑文
  searchInscriptions(keyword) {
    if (!keyword) return this.featuredInscriptions;
    const lowerKeyword = keyword.toLowerCase();
    return this.featuredInscriptions.filter(
      (item) =>
        item.title.toLowerCase().includes(lowerKeyword) ||
        item.description.toLowerCase().includes(lowerKeyword) ||
        item.dynasty.toLowerCase().includes(lowerKeyword) ||
        item.location.toLowerCase().includes(lowerKeyword)
    );
  },
};
