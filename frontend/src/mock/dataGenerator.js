/**
 * Mock数据生成器
 * 生成符合API规范的测试数据
 */

// ==================== 基础工具 ====================
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomChoice = (arr) => arr[randomInt(0, arr.length - 1)];
const randomDate = (start, end) => new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));

const generateId = (prefix = '') => `${prefix}${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// 常用数据
const dynasties = ['汉代', '唐代', '宋代', '明代', '清代', '魏晋', '南北朝'];
const categories = ['书法艺术', '历史人物', '文学碑刻', '宗教碑刻', '建筑铭文'];
const inscriptionTypes = ['墓碑文', '功德碑', '题记', '摩崖石刻', '匾额', '楹联'];
const cities = ['西安', '洛阳', '北京', '南京', '杭州', '开封', '成都', '长沙'];

// ==================== 用户数据 ====================
export const generateUser = () => ({
  id: generateId('user_'),
  name: randomChoice(['张三', '李四', '王五', '赵六', '刘七', '陈八']),
  email: `user${randomInt(1000, 9999)}@example.com`,
  phone: `138${randomInt(10000000, 99999999)}`,
  avatar: `https://i.pravatar.cc/150?img=${randomInt(1, 70)}`,
  stats: {
    total_recognitions: randomInt(10, 200),
    total_favorites: randomInt(5, 50),
    total_questions: randomInt(1, 30)
  },
  created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString(),
  is_verified: Math.random() > 0.3,
  last_login: randomDate(new Date(2024, 0, 1), new Date()).toISOString()
});

// ==================== 识别记录数据 ====================
export const generateRecognitionRecord = () => ({
  id: generateId('rec_'),
  title: randomChoice(['李白墓碑文', '颜真卿书法', '多宝塔碑', '玄奘法师碑', '王羲之书法']),
  image_id: generateId('img_'),
  image_url: `https://picsum.photos/800/600?random=${randomInt(1, 1000)}`,
  original_text: randomChoice([
    '维大唐开元二十有九年秋九月十五日，太白居士李白之墓',
    '臣本布衣，躬耕于南阳，苟全性命于乱世',
    '大慈恩寺三藏法师玄奘，俗姓陈氏，字祎河',
    '会稽内史王羲之，永和九年暮春之初',
    '故太子太傅颜真卿，鲁郡开国公'
  ]),
  modern_text: randomChoice([
    '大唐开元二十九年秋九月十五日，太白居士李白之墓',
    '臣本布衣，躬耕于南阳，苟全性命于乱世',
    '大慈恩寺三藏法师玄奘，俗姓陈氏，字祎河',
    '会稽内史王羲之，永和九年暮春之初',
    '故太子太傅颜真卿，鲁郡开国公'
  ]),
  confidence: randomInt(85, 99) + Math.random(),
  word_count: randomInt(20, 200),
  dynasty: randomChoice(dynasties),
  period: randomChoice(['开元年间', '建元年间', '永和年间', '贞观年间']),
  location: randomChoice(cities),
  person: randomChoice(['李白', '诸葛亮', '玄奘', '王羲之', '颜真卿']),
  estimated_year: `公元${randomInt(100, 1800)}年`,
  processing_time: randomInt(10, 60),
  created_at: randomDate(new Date(2024, 0, 1), new Date()).toISOString(),
  is_favorited: Math.random() > 0.7,
  tags: randomChoice([
    ['李白', '唐代', '诗仙'],
    ['诸葛亮', '三国', '智慧'],
    ['玄奘', '唐代', '佛教'],
    ['王羲之', '东晋', '书圣'],
    ['颜真卿', '唐代', '书法']
  ])
});

// ==================== AI阐释数据 ====================
export const generateAIInterpretation = () => ({
  interpretation_id: generateId('int_'),
  results: {
    history: {
      title: '历史背景',
      content: randomChoice([
        '这块碑文记录的是唐代诗仙李白的生平事迹，反映了盛唐时期的文学繁荣和诗人地位。李白生活在唐朝开元年间，这是中国历史上的黄金时期，文化艺术达到了前所未有的高度。',
        '该碑文记录了三国时期蜀汉丞相诸葛亮的生平，体现出古代文人的理想品格和治国理念。诸葛亮作为智慧的化身，在历史上留下了深远的影响。',
        '此碑为玄奘法师所立，记录了其西天取经的壮举。作为唐代著名高僧，玄奘为佛教在中国的传播和发展做出了巨大贡献。'
      ]),
      key_points: randomChoice([
        ['李白生平', '开元盛世', '唐代文学'],
        ['三国历史', '蜀汉政权', '古代智慧'],
        ['佛教历史', '西天取经', '文化交流']
      ])
    },
    culture: {
      title: '文化意义',
      content: randomChoice([
        '碑文体现了唐代的文化特色，包括对文人雅士的推崇、对诗歌艺术的重视，以及对社会制度的思考。',
        '该碑文反映了三国时期儒家文化的影响，以及君子修身齐家治国平天下的理想追求。',
        '此碑体现了佛教文化的包容性和传播性，以及唐代对外文化交流的开放态度。'
      ]),
      keywords: randomChoice([
        ['唐代文化', '文人地位', '文学传统'],
        ['儒家思想', '君子之道', '治国理念'],
        ['佛教文化', '对外交流', '文化传播']
      ])
    },
    literature: {
      title: '文学价值',
      content: randomChoice([
        '从文学角度看，这块碑文具有重要价值。碑文采用骈文体裁，文字优美，结构严谨，体现了唐代碑文的特点。',
        '该碑文在文学史上具有重要地位，其文笔流畅，寓意深刻，为后世文学创作提供了重要参考。',
        '此碑的文学价值体现在其独特的叙述方式和深刻的思想内涵，为研究古代文学发展提供了珍贵资料。'
      ]),
      style: randomChoice(['骈文体', '记叙文', '议论文']),
      themes: randomChoice([
        ['人生感悟', '文学成就', '社会理想'],
        ['忠诚品格', '智慧人生', '政治理想'],
        ['修行感悟', '文化传播', '精神追求']
      ])
    }
  },
  related_inscriptions: [
    {
      id: generateId('rec_'),
      title: randomChoice(['杜甫墓志铭', '白居易碑文', '苏轼题记']),
      similarity: randomInt(70, 95) / 100
    }
  ]
});

// ==================== 对话数据 ====================
export const generateChatMessage = () => ({
  conversation_id: generateId('conv_'),
  reply: {
    content: randomChoice([
      "'维'在古文中是一个发语词，常用于碑文的开头，表示'至于'、'话说'的意思。在唐代碑文中，这种用法非常普遍，体现了古代汉语的语法特点。",
      "'开元'是唐玄宗的年号，开元年间(713-741年)是唐朝最为繁荣的时期，被誉为'开元盛世'。这一时期的文化艺术发展到了一个新的高度。",
      "李白的诗歌风格豪放飘逸，被誉为'诗仙'。这首墓碑文虽然简短，但已经体现出李白诗歌的一些特点，如语言的凝练和意境的深远。"
    ]),
    type: 'text',
    sources: [
      {
        title: '古代汉语虚词研究',
        url: `https://example.com/article/${randomInt(1, 100)}`
      },
      {
        title: '唐代文学史',
        url: `https://example.com/article/${randomInt(1, 100)}`
      }
    ],
    suggestions: randomChoice([
      ['唐代常用发语词有哪些？', '这块碑文的其他虚词解释'],
      ['开元盛世有什么特点？', '唐代年号的使用规律'],
      ['李白诗歌的风格特点？', '唐代诗人墓碑文的特色']
    ])
  },
  related_questions: [
    {
      question: randomChoice([
        '唐代碑文有什么特点？',
        '古代碑文的文体格式是怎样的？',
        '如何理解古文中的虚词用法？'
      ]),
      confidence: randomInt(80, 95) / 100
    }
  ]
});

// ==================== 知识库文章数据 ====================
export const generateArticle = () => {
  // 首先获取标题，避免在对象字面量中调用函数
  const titles = [
    '唐代楷书的发展与特点',
    '中国古代碑刻艺术概览',
    '李白诗歌的艺术成就',
    '玄奘法师与佛教传播',
    '王羲之书法艺术赏析',
    '唐代文化的繁荣与特点',
    '古代碑文的文体格式研究',
    '中国书法史上的重要碑刻'
  ];
  
  const title = randomChoice(titles);
  
  return {
    id: randomInt(100, 999),
    title: title,
    content: `# ${title}

## 概述

${randomChoice([
  '唐代是中国书法史上的黄金时期，楷书在这一时期得到了空前的发展和繁荣。',
  '中国古代碑刻艺术源远流长，是中华文明的重要组成部分。',
  '李白作为唐代最伟大的诗人，其诗歌成就对后世产生了深远的影响。'
])}

## 正文内容

${randomChoice([
  '在唐代，楷书已经成为官方文书的主要字体。这一时期出现了许多杰出的楷书大家，如颜真卿、柳公权等。',
  '碑刻艺术不仅记录了历史，也展现了不同朝代的艺术风格和文化特色。',
  '李白的诗歌语言豪放，想象丰富，体现了唐代开放包容的文化精神。'
])}

## 总结

通过对这些碑文的研究，我们可以更好地理解古代文化的传承和发展脉络。`,
    excerpt: randomChoice([
      '唐代楷书在中国书法史上占据重要地位，以其规范、工整的特点著称。',
      '中国古代碑刻艺术体现了深厚的历史文化内涵，是研究古代社会的重要资料。',
      '李白诗歌的艺术成就代表了唐代文学的最高水平，影响至今。'
    ]),
    cover_image: `https://picsum.photos/400/300?random=${randomInt(1, 1000)}`,
    author: {
      name: randomChoice(['王教授', '李研究员', '张学者', '陈博士']),
      avatar: `https://i.pravatar.cc/100?img=${randomInt(1, 20)}`,
      title: randomChoice(['书法研究所研究员', '文学系教授', '历史学博士', '文物研究专家'])
    },
    metadata: {
      category: randomChoice(categories),
      tags: randomChoice([
        ['唐代', '楷书', '书法'],
        ['古代文化', '碑刻', '历史'],
        ['李白', '诗歌', '唐代文学'],
        ['佛教', '玄奘', '文化交流'],
        ['王羲之', '书法', '艺术']
      ]),
      read_time: randomInt(3, 15),
      word_count: randomInt(1500, 5000),
      publish_date: randomDate(new Date(2024, 0, 1), new Date()).toISOString().split('T')[0],
      last_updated: randomDate(new Date(2024, 0, 1), new Date()).toISOString()
    },
    stats: {
      views: randomInt(500, 5000),
      likes: randomInt(50, 300),
      comments: randomInt(5, 50),
      bookmarks: randomInt(20, 100)
    }
  };
};

// ==================== 朝代数据 ====================
export const generateDynasty = () => ({
  id: generateId('dynasty_'),
  name: randomChoice(dynasties),
  period: randomChoice([
    '公元前206年-公元220年',
    '公元618年-公元907年',
    '公元960年-公元1279年',
    '公元1368年-公元1644年',
    '公元1644年-公元1912年'
  ]),
  description: randomChoice([
    '汉代是中国历史上的重要朝代，在文化、科技、艺术等方面都有很大发展。',
    '唐代是中国历史上的盛世，文化繁荣，包容开放，诗歌艺术达到高峰。',
    '宋代在文化、科技、经济等方面都有显著发展，理学兴起，文学艺术繁荣。',
    '明代在文学、艺术、科技等方面都有重要贡献，出现了许多杰出人物。',
    '清代是中国历史上最后一个封建王朝，在文学艺术方面有其独特成就。'
  ]),
  characteristics: randomChoice([
    ['政治统一', '文化繁荣', '科技发展'],
    ['开放包容', '诗歌鼎盛', '书法艺术'],
    ['理学兴起', '科技发达', '文学繁荣'],
    ['小说兴起', '戏曲发展', '文化传承'],
    ['小说创作', '戏曲发展', '文化整理']
  ]),
  representative_figures: randomChoice([
    ['刘邦', '司马迁', '张衡'],
    ['李世民', '李白', '杜甫', '颜真卿'],
    ['苏轼', '李清照', '岳飞'],
    ['朱元璋', '郑和', '李时珍'],
    ['康熙', '乾隆', '曹雪芹']
  ]),
  inscription_count: randomInt(100, 1000),
  image_url: `https://picsum.photos/600/400?random=${randomInt(1, 100)}`
});

// ==================== 收藏数据 ====================
export const generateFavorite = () => ({
  id: generateId('fav_'),
  type: randomChoice(['inscription', 'article']),
  item: randomChoice([
    generateRecognitionRecord(),
    generateArticle()
  ]),
  notes: randomChoice([
    '很有价值的碑文',
    '字体优美，值得学习',
    '历史意义重大',
    '文学价值很高',
    '书法艺术精品'
  ]),
  tags: randomChoice([
    ['重要', '珍贵'],
    ['学习', '研究'],
    ['收藏', '精品'],
    ['推荐', '必读'],
    ['经典', '名作']
  ]),
  created_at: randomDate(new Date(2024, 0, 1), new Date()).toISOString()
});

// ==================== 通知数据 ====================
export const generateNotification = () => ({
  id: generateId('notif_'),
  type: randomChoice(['system', 'recognition', 'ai', 'social']),
  title: randomChoice([
    '识别完成通知',
    'AI阐释已生成',
    '系统维护通知',
    '新功能上线',
    '识别质量提升'
  ]),
  message: randomChoice([
    '您的碑文识别任务已完成，请查看结果。',
    'AI已经为您的碑文生成了详细的阐释。',
    '系统将于今晚进行维护升级。',
    '新的校对功能已经上线，欢迎使用。',
    '识别准确率已提升至98%以上。'
  ]),
  is_read: Math.random() > 0.7,
  action_url: `/recognition/${generateId('rec_')}`,
  created_at: randomDate(new Date(2024, 0, 1), new Date()).toISOString(),
  expires_at: randomDate(new Date(), new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)).toISOString()
});

// ==================== 统计数据 ====================
export const generateStats = () => ({
  recognition_stats: {
    total_count: randomInt(100, 1000),
    this_month: randomInt(20, 100),
    by_dynasty: {
      '唐代': randomInt(50, 150),
      '汉代': randomInt(30, 100),
      '宋代': randomInt(20, 80),
      '明代': randomInt(15, 60),
      '清代': randomInt(10, 40)
    },
    average_confidence: randomInt(90, 99) + Math.random()
  },
  activity_stats: {
    favorites_count: randomInt(10, 100),
    questions_asked: randomInt(5, 50),
    articles_read: randomInt(20, 200),
    last_active: randomDate(new Date(2024, 0, 1), new Date()).toISOString()
  },
  growth_trend: Array.from({ length: 7 }, (_, i) => ({
    date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    count: randomInt(1, 10)
  }))
});

// ==================== 批量生成器 ====================
export const generateRecognitionList = (count = 20) => 
  Array.from({ length: count }, () => generateRecognitionRecord());

export const generateArticleList = (count = 10) => 
  Array.from({ length: count }, () => generateArticle());

export const generateFavoriteList = (count = 15) => 
  Array.from({ length: count }, () => generateFavorite());

export const generateNotificationList = (count = 10) => 
  Array.from({ length: count }, () => generateNotification());

export const generateDynastyList = () => dynasties.map(dynasty => ({
  id: generateId('dynasty_'),
  name: dynasty,
  count: randomInt(10, 200)
}));

// ==================== 分页数据 ====================
export const generatePaginatedResponse = (data, page = 1, perPage = 20) => ({
  data: data.slice((page - 1) * perPage, page * perPage),
  pagination: {
    current_page: page,
    per_page: perPage,
    total_count: data.length,
    total_pages: Math.ceil(data.length / perPage)
  }
});

// ==================== 错误模拟 ====================
export const generateError = (code = 400, message = '请求失败') => ({
  success: false,
  error: {
    code: `ERROR_${code}`,
    message,
    details: null
  },
  timestamp: new Date().toISOString()
});

export default {
  generateUser,
  generateRecognitionRecord,
  generateAIInterpretation,
  generateChatMessage,
  generateArticle,
  generateDynasty,
  generateFavorite,
  generateNotification,
  generateStats,
  generateRecognitionList,
  generateArticleList,
  generateFavoriteList,
  generateNotificationList,
  generateDynastyList,
  generatePaginatedResponse,
  generateError
};