const kokuyo_line_front = {
    name: "kokuyo-line-front",
    columns: 1,
    textFrame: [[150, 80, 770]], // 上边界, 左边界, 右边界
    fontSize: 32,
    lineHeight: 35.2,
    lineFrame: [178, 63, 776],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 25,
    smartPunctuation: true,
    showLines: true,
    background: "bg/kokuyo-line-front.png",
    nextPage: "kokuyo-line-back",
    additional: [
        [2.5, "#c3d0dd", 63, 1057, 776, 1057]
    ]
};

const kokuyo_line_back = {
    name: "kokuyo-line-back",
    columns: 1,
    textFrame: [[149, 24, 715]], // 上边界, 左边界, 右边界
    fontSize: 32,
    lineHeight: 35.2,
    lineFrame: [177, 10, 723],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 25,
    smartPunctuation: true,
    showLines: true,
    background: "bg/kokuyo-line-back.png",
    nextPage: "kokuyo-line-front",
    additional: [
        [2.5, "#c3d0dd", 10, 1056, 723, 1056]
    ]
};

const kokuyo_line_front_2_columns = {
    name: "kokuyo-line-front-2-columns",
    columns: 2,
    textFrame: [[150, 80, 410], [150, 430, 770]], // 上边界, 左边界, 右边界
    fontSize: 32,
    lineHeight: 35.2,
    lineFrame: [178, 63, 776],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 25,
    smartPunctuation: true,
    showLines: true,
    background: "bg/kokuyo-line-front.png",
    nextPage: "kokuyo-line-back-2-columns",
    additional: [
        [2.5, "#c3d0dd", 63, 1057, 776, 1057]
    ]
};

const kokuyo_line_back_2_columns = {
    name: "kokuyo-line-back-2-columns",
    columns: 2,
    textFrame: [[149, 24, 370], [149, 385, 720]], // 上边界, 左边界, 右边界
    fontSize: 32,
    lineHeight: 35.2,
    lineFrame: [177, 10, 723],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 25,
    smartPunctuation: true,
    showLines: true,
    background: "bg/kokuyo-line-back.png",
    nextPage: "kokuyo-line-front-2-columns",
    additional: [
        [2.5, "#c3d0dd", 10, 1056, 723, 1056]
    ]
};

const english_guided_writing_shs = {
    name: "english-guided-writing-shs",
    columns: 3,
    textFrame: [[158, 20, 380], [78, 420, 780], [789, 420, 780]], // 上边界, 左边界, 右边界
    fontSize: 26,
    lineHeight: 39.5,
    lineFrame: [177, 10, 723],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 17,
    smartPunctuation: true,
    showLines: false,
    background: "bg/english-guided-writing-shs.jpg",
    nextPage: "english-guided-writing-shs"
};

const yimo_front = {
    name: "yimo-front",
    columns: 1,
    textFrame: [[150, 80, 600]], // 上边界, 左边界, 右边界
    fontSize: 32,
    lineHeight: 35.2,
    lineFrame: [178, 63, 776],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 25,
    smartPunctuation: true,
    showLines: true,
    background: "bg/kokuyo-line-front.png",
    nextPage: "yimo-back",
    additional: [
        [2.5, "#c3d0dd", 63, 1057, 776, 1057]
    ]
};

const yimo_back = {
    name: "yimo-back",
    columns: 1,
    textFrame: [[149, 200, 715]], // 上边界, 左边界, 右边界
    fontSize: 32,
    lineHeight: 35.2,
    lineFrame: [177, 10, 723],
    lineWidth: 2,
    lineColor: "#dedede",
    lineCount: 25,
    smartPunctuation: true,
    showLines: true,
    background: "bg/kokuyo-line-back.png",
    nextPage: "yimo-front",
    additional: [
        [2.5, "#c3d0dd", 10, 1056, 723, 1056]
    ]
};


const config_dict = {
    "kokuyo-line-front": kokuyo_line_front,
    "kokuyo-line-back": kokuyo_line_back,
    "kokuyo-line-front-2-columns": kokuyo_line_front_2_columns,
    "kokuyo-line-back-2-columns": kokuyo_line_back_2_columns,
    "english-guided-writing-shs": english_guided_writing_shs,
    "yimo-front": yimo_front,
    "yimo-back": yimo_back
}