import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import './TetrisPage.css';

const ROWS = 20;
const COLS = 10;

const TETROMINOES = {
  I: { shape: [[1,1,1,1]], color: 'I' },
  O: { shape: [[1,1],[1,1]], color: 'O' },
  T: { shape: [[0,1,0],[1,1,1]], color: 'T' },
  S: { shape: [[0,1,1],[1,1,0]], color: 'S' },
  Z: { shape: [[1,1,0],[0,1,1]], color: 'Z' },
  J: { shape: [[1,0,0],[1,1,1]], color: 'J' },
  L: { shape: [[0,0,1],[1,1,1]], color: 'L' },
};

const PIECE_NAMES = Object.keys(TETROMINOES);

const createEmptyBoard = () =>
  Array.from({ length: ROWS }, () => Array(COLS).fill(null));

const randomPiece = () => {
  const name = PIECE_NAMES[Math.floor(Math.random() * PIECE_NAMES.length)];
  return { ...TETROMINOES[name], name };
};

const rotateCW = (matrix) => {
  const rows = matrix.length;
  const cols = matrix[0].length;
  const rotated = Array.from({ length: cols }, () => Array(rows).fill(0));
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      rotated[c][rows - 1 - r] = matrix[r][c];
    }
  }
  return rotated;
};

const isValidPosition = (board, shape, pos) => {
  for (let r = 0; r < shape.length; r++) {
    for (let c = 0; c < shape[r].length; c++) {
      if (!shape[r][c]) continue;
      const newR = pos.row + r;
      const newC = pos.col + c;
      if (newR < 0 || newR >= ROWS || newC < 0 || newC >= COLS) return false;
      if (board[newR][newC]) return false;
    }
  }
  return true;
};

const getGhostPosition = (board, shape, pos) => {
  let ghostRow = pos.row;
  while (isValidPosition(board, shape, { row: ghostRow + 1, col: pos.col })) {
    ghostRow++;
  }
  return { row: ghostRow, col: pos.col };
};

const getDropSpeed = (level) => Math.max(100, 800 - (level - 1) * 70);

const TetrisPage = () => {
  const [board, setBoard] = useState(createEmptyBoard);
  const [currentPiece, setCurrentPiece] = useState(null);
  const [currentPos, setCurrentPos] = useState({ row: 0, col: 0 });
  const [nextPiece, setNextPiece] = useState(null);
  const [score, setScore] = useState(0);
  const [lines, setLines] = useState(0);
  const [level, setLevel] = useState(1);
  const [gameOver, setGameOver] = useState(false);
  const [paused, setPaused] = useState(false);
  const [started, setStarted] = useState(false);

  const gs = useRef({
    board: createEmptyBoard(),
    currentPiece: null,
    currentPos: { row: 0, col: 0 },
    gameOver: false,
    paused: false,
    level: 1,
    nextPiece: null,
  });
  const dropTimerRef = useRef(null);

  useEffect(() => { gs.current.board = board; }, [board]);
  useEffect(() => { gs.current.currentPiece = currentPiece; }, [currentPiece]);
  useEffect(() => { gs.current.currentPos = currentPos; }, [currentPos]);
  useEffect(() => { gs.current.gameOver = gameOver; }, [gameOver]);
  useEffect(() => { gs.current.paused = paused; }, [paused]);
  useEffect(() => { gs.current.level = level; }, [level]);
  useEffect(() => { gs.current.nextPiece = nextPiece; }, [nextPiece]);

  const lockPiece = useCallback(() => {
    const s = gs.current;
    const piece = s.currentPiece;
    const pos = s.currentPos;
    if (!piece) return;

    const newBoard = s.board.map((row) => [...row]);
    for (let r = 0; r < piece.shape.length; r++) {
      for (let c = 0; c < piece.shape[r].length; c++) {
        if (piece.shape[r][c]) {
          const boardR = pos.row + r;
          const boardC = pos.col + c;
          if (boardR >= 0 && boardR < ROWS) {
            newBoard[boardR][boardC] = piece.color;
          }
        }
      }
    }

    const clearedLines = [];
    for (let r = ROWS - 1; r >= 0; r--) {
      if (newBoard[r].every((cell) => cell !== null)) {
        clearedLines.push(r);
      }
    }

    if (clearedLines.length > 0) {
      for (const lineIdx of clearedLines) {
        newBoard.splice(lineIdx, 1);
        newBoard.unshift(Array(COLS).fill(null));
      }
      const lineScores = [0, 100, 300, 500, 800];
      const lvl = s.level;
      setScore((prev) => prev + (lineScores[clearedLines.length] || 0) * lvl);
      setLines((prev) => {
        const newLines = prev + clearedLines.length;
        setLevel(Math.floor(newLines / 10) + 1);
        return newLines;
      });
    }

    setBoard(newBoard);
    gs.current.board = newBoard;

    // Spawn next piece directly
    const next = s.nextPiece;
    if (next) {
      const spawnCol = Math.floor((COLS - next.shape[0].length) / 2);
      const spawnPos = { row: 0, col: spawnCol };
      if (!isValidPosition(newBoard, next.shape, spawnPos)) {
        setGameOver(true);
        setCurrentPiece(null);
        return;
      }
      const newNext = randomPiece();
      setCurrentPiece(next);
      setCurrentPos(spawnPos);
      setNextPiece(newNext);
    }
  }, []);

  const moveDown = useCallback(() => {
    const s = gs.current;
    if (s.gameOver || s.paused || !s.currentPiece) return;
    const newPos = { row: s.currentPos.row + 1, col: s.currentPos.col };
    if (isValidPosition(s.board, s.currentPiece.shape, newPos)) {
      setCurrentPos(newPos);
    } else {
      lockPiece();
    }
  }, [lockPiece]);

  const moveLeft = useCallback(() => {
    const s = gs.current;
    if (s.gameOver || s.paused || !s.currentPiece) return;
    const newPos = { row: s.currentPos.row, col: s.currentPos.col - 1 };
    if (isValidPosition(s.board, s.currentPiece.shape, newPos)) {
      setCurrentPos(newPos);
    }
  }, []);

  const moveRight = useCallback(() => {
    const s = gs.current;
    if (s.gameOver || s.paused || !s.currentPiece) return;
    const newPos = { row: s.currentPos.row, col: s.currentPos.col + 1 };
    if (isValidPosition(s.board, s.currentPiece.shape, newPos)) {
      setCurrentPos(newPos);
    }
  }, []);

  const rotatePiece = useCallback(() => {
    const s = gs.current;
    if (s.gameOver || s.paused || !s.currentPiece) return;
    const rotated = rotateCW(s.currentPiece.shape);
    const kicks = [0, -1, 1, -2, 2];
    for (const kick of kicks) {
      const newPos = { row: s.currentPos.row, col: s.currentPos.col + kick };
      if (isValidPosition(s.board, rotated, newPos)) {
        setCurrentPiece({ ...s.currentPiece, shape: rotated });
        setCurrentPos(newPos);
        return;
      }
    }
  }, []);

  const hardDrop = useCallback(() => {
    const s = gs.current;
    if (s.gameOver || s.paused || !s.currentPiece) return;
    const ghost = getGhostPosition(s.board, s.currentPiece.shape, s.currentPos);
    const dropDistance = ghost.row - s.currentPos.row;
    setScore((prev) => prev + dropDistance * 2);
    // Update ref and state, then lock
    gs.current.currentPos = ghost;
    setCurrentPos(ghost);
    setTimeout(() => lockPiece(), 0);
  }, [lockPiece]);

  const togglePause = useCallback(() => {
    if (gs.current.gameOver || !started) return;
    setPaused((p) => !p);
  }, [started]);

  const startGame = useCallback(() => {
    const emptyBoard = createEmptyBoard();
    setBoard(emptyBoard);
    setScore(0);
    setLines(0);
    setLevel(1);
    setGameOver(false);
    setPaused(false);
    setStarted(true);

    gs.current.board = emptyBoard;
    gs.current.gameOver = false;
    gs.current.paused = false;
    gs.current.level = 1;

    const first = randomPiece();
    const second = randomPiece();
    const spawnCol = Math.floor((COLS - first.shape[0].length) / 2);
    setCurrentPiece(first);
    setCurrentPos({ row: 0, col: spawnCol });
    setNextPiece(second);
    gs.current.nextPiece = second;
  }, []);

  // Drop timer
  useEffect(() => {
    if (!started || gameOver || paused) {
      clearInterval(dropTimerRef.current);
      return;
    }
    dropTimerRef.current = setInterval(() => {
      moveDown();
    }, getDropSpeed(level));
    return () => clearInterval(dropTimerRef.current);
  }, [started, gameOver, paused, level, moveDown]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!started) return;
      switch (e.key) {
        case 'ArrowLeft':  e.preventDefault(); moveLeft(); break;
        case 'ArrowRight': e.preventDefault(); moveRight(); break;
        case 'ArrowDown':  e.preventDefault(); moveDown(); break;
        case 'ArrowUp':    e.preventDefault(); rotatePiece(); break;
        case ' ':          e.preventDefault(); hardDrop(); break;
        case 'p': case 'P': e.preventDefault(); togglePause(); break;
        default: break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [started, moveLeft, moveRight, moveDown, rotatePiece, hardDrop, togglePause]);

  const renderBoard = () => {
    const display = board.map((row) => [...row]);

    if (currentPiece && !gameOver) {
      const ghost = getGhostPosition(board, currentPiece.shape, currentPos);
      if (ghost.row !== currentPos.row) {
        for (let r = 0; r < currentPiece.shape.length; r++) {
          for (let c = 0; c < currentPiece.shape[r].length; c++) {
            if (currentPiece.shape[r][c]) {
              const gr = ghost.row + r;
              const gc = ghost.col + c;
              if (gr >= 0 && gr < ROWS && gc >= 0 && gc < COLS && !display[gr][gc]) {
                display[gr][gc] = `ghost-${currentPiece.color}`;
              }
            }
          }
        }
      }
      for (let r = 0; r < currentPiece.shape.length; r++) {
        for (let c = 0; c < currentPiece.shape[r].length; c++) {
          if (currentPiece.shape[r][c]) {
            const br = currentPos.row + r;
            const bc = currentPos.col + c;
            if (br >= 0 && br < ROWS && bc >= 0 && bc < COLS) {
              display[br][bc] = currentPiece.color;
            }
          }
        }
      }
    }

    return display.flat().map((cell, i) => {
      const isGhost = typeof cell === 'string' && cell.startsWith('ghost-');
      const color = isGhost ? cell.replace('ghost-', '') : cell;
      return (
        <div
          key={i}
          className={`tetris-cell${cell ? ' filled' : ''}${color ? ` ${color}` : ''}${isGhost ? ' ghost' : ''}`}
        />
      );
    });
  };

  const renderNextPiece = () => {
    const grid = Array.from({ length: 4 }, () => Array(4).fill(null));
    if (nextPiece) {
      const offsetR = Math.floor((4 - nextPiece.shape.length) / 2);
      const offsetC = Math.floor((4 - nextPiece.shape[0].length) / 2);
      for (let r = 0; r < nextPiece.shape.length; r++) {
        for (let c = 0; c < nextPiece.shape[r].length; c++) {
          if (nextPiece.shape[r][c]) {
            grid[offsetR + r][offsetC + c] = nextPiece.color;
          }
        }
      }
    }
    return grid.flat().map((cell, i) => (
      <div key={i} className={`next-cell${cell ? ` filled ${cell}` : ''}`} />
    ));
  };

  return (
    <div className="tetris-page">
      <Link to="/dashboard" className="back-link">
        &larr; 返回
      </Link>
      <div className="tetris-wrapper">
        <div className="tetris-main">
          <h1 className="tetris-title">Tetris</h1>
          <div className="board-wrapper">
            <div className="tetris-board">{renderBoard()}</div>
            {gameOver && (
              <div className="game-over-overlay">
                <h2>游戏结束</h2>
                <p>得分: {score}</p>
                <button onClick={startGame}>再来一局</button>
              </div>
            )}
            {paused && !gameOver && (
              <div className="pause-overlay">
                <h2>已暂停</h2>
              </div>
            )}
          </div>
          <div className="tetris-controls">
            {!started ? (
              <button className="primary" onClick={startGame}>
                开始游戏
              </button>
            ) : (
              <>
                <button onClick={togglePause}>
                  {paused ? '继续' : '暂停'}
                </button>
                <button onClick={startGame}>重新开始</button>
              </>
            )}
          </div>
        </div>

        <div className="tetris-sidebar">
          <div className="side-panel">
            <h3>下一个</h3>
            <div className="next-piece-grid">{renderNextPiece()}</div>
          </div>

          <div className="side-panel">
            <div className="stat-row">
              <span className="label">分数</span>
              <span className="value">{score}</span>
            </div>
            <div className="stat-row">
              <span className="label">行数</span>
              <span className="value">{lines}</span>
            </div>
            <div className="stat-row">
              <span className="label">等级</span>
              <span className="value">{level}</span>
            </div>
          </div>

          <div className="side-panel">
            <h3>操作</h3>
            <div className="key-hints">
              <span className="key">&larr; &rarr;</span>
              <span className="desc">左右移动</span>
              <span className="key">&darr;</span>
              <span className="desc">加速下落</span>
              <span className="key">&uarr;</span>
              <span className="desc">旋转</span>
              <span className="key">Space</span>
              <span className="desc">硬降</span>
              <span className="key">P</span>
              <span className="desc">暂停</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TetrisPage;
