# Phat Live - Đá Gà Trực Tiếp

## 1. Concept & Vision

Một trang web xem đá gà trực tiếp với giao diện mobile-first, tối ưu cho điện thoại. Phong cách bold, năng động với màu sắc rực rỡ của sàn đấu. Cảm giác như đang ở trong sới đá gà thực thụ - căng thẳng, kịch tính và hồi hộp.

## 2. Design Language

### Aesthetic Direction
Dark gaming aesthetic với accent màu đỏ/cam rực rỡ - phong cách "fight club" cho người yêu đá gà.

### Color Palette
- **Primary**: `#FF4500` (Orange Red - năng lượng, chiến đấu)
- **Secondary**: `#1A1A2E` (Dark Navy - nền chính)
- **Accent**: `#FFD700` (Gold - chiến thắng, vinh quang)
- **Background**: `#0F0F1A` (Deep Dark)
- **Surface**: `#16213E` (Card background)
- **Text Primary**: `#FFFFFF`
- **Text Secondary**: `#A0A0B0`
- **Success**: `#00C853`
- **Danger**: `#FF1744`

### Typography
- **Headings**: "Russo One", sans-serif - bold, gaming feel
- **Body**: "Quicksand", sans-serif - dễ đọc, hiện đại
- **Accent text**: "Bebas Neue", sans-serif - cho số liệu, thống kê

### Spatial System
- Base unit: 8px
- Mobile padding: 16px
- Card gap: 12px
- Border radius: 12px (cards), 8px (buttons)

### Motion Philosophy
- Pulse animation cho trạng thái LIVE
- Smooth slide-in cho nội dung mới
- Subtle hover scale (1.02) cho interactive elements
- Glow effect cho các elements quan trọng

### Visual Assets
- Lucide icons cho UI elements
- Gradient overlays cho cards
- Animated live indicator (pulsing red dot)
- Custom badge cho trạng thái trận đấu

## 3. Layout & Structure

### Mobile-First Layout (320px - 480px primary)
```
┌─────────────────────────┐
│  🔴 LIVE   [Logo]  ☰   │  <- Sticky header
├─────────────────────────┤
│  [Arena Tabs]           │  <- Horizontal scroll tabs
│  CPC2 | CPC3 | CPC4... │
├─────────────────────────┤
│  ┌─────────────────┐    │
│  │  🔴 LIVE        │    │
│  │  [Video Player] │    │  <- Main video (16:9)
│  │                 │    │
│  └─────────────────┘    │
│                         │
│  Match Info Card        │
│  ┌─────────────────┐    │
│  │ 🔴 Meron  vs  Wala │  │
│  │ 0.95    BDD   0.87 │  │
│  └─────────────────┘    │
├─────────────────────────┤
│  Danh Sách Trận         │
│  ┌─────────────────┐    │
│  │ Trận 17 | CPC2  │    │
│  └─────────────────┘    │
│  ┌─────────────────┐    │
│  │ Trận 16 | CPC2  │    │
│  └─────────────────┘    │
│         ...              │
└─────────────────────────┘
```

### Responsive Breakpoints
- Mobile: 320px - 480px (primary target)
- Tablet: 481px - 768px
- Desktop: 769px+ (centered max-width 480px for mobile simulation)

## 4. Features & Interactions

### Core Features

#### 1. Arena Tabs
- Horizontal scrollable tabs: CPC2, CPC3, CPC4, CPC5, Xà Xía, Thường Phước
- Active tab has underline + primary color
- Tap to switch arena (instant, no loading)

#### 2. Main Video Player
- 16:9 aspect ratio container
- Simulated live stream với placeholder
- Overlay controls: mute, fullscreen, quality selector
- LIVE badge animation (pulsing)
- Current match info overlay

#### 3. Match Info Card
- Shows current/recent match
- Display odds for: Meron (red), Wala (blue), BDD (yellow)
- Match time and arena info
- Rooster names if available

#### 4. Match List
- Scrollable list of recent/upcoming matches
- Each item shows: match number, arena, status (LIVE/SCHEDULED/ENDED)
- Tap to select match and load in main player
- Visual indicator for LIVE matches

#### 5. Simple Chat (Optional Display)
- Show latest comments
- Auto-scroll newest
- Input field at bottom (non-functional placeholder)

### Interaction Details

| Action | Result |
|--------|--------|
| Tap arena tab | Switch to that arena, update match list |
| Tap match item | Load match in main player |
| Tap video player | Toggle play/pause (simulated) |
| Long press video | Show quality options |
| Pull down match list | Refresh matches |

### States

**Empty State**: "Không có trận đấu đang diễn ra" with refresh button

**Loading State**: Skeleton cards with pulse animation

**Error State**: "Không thể kết nối. Vui lòng thử lại." with retry button

## 5. Component Inventory

### Header
- Height: 56px
- Background: Surface color with blur
- Logo text: "PHAT LIVE" in Russo One
- LIVE indicator: Red pulsing dot + "LIVE" text
- Menu icon: Hamburger (non-functional, visual only)

### Arena Tabs
- Height: 48px
- Horizontal scroll, no scrollbar visible
- Tab item: Padding 16px horizontal
- Active: Primary color underline, bold text
- Inactive: Text secondary color

### Video Player Card
- Aspect ratio: 16:9
- Border radius: 12px
- Shadow: Large elevated
- Overlay gradient: Bottom 30% black gradient for readability
- LIVE badge: Top-left, red with white text, pulse animation
- Controls: Semi-transparent bottom bar

### Match Info Card
- Background: Surface with subtle border
- Arena badge: Small pill with arena name
- VS display: Large "VS" text in accent color
- Odds row: 3 columns for Meron/Wala/BDD
- Each odds: Colored pill (red/blue/yellow)

### Match List Item
- Height: 72px
- Left: Match thumbnail (16:9, 80px wide)
- Center: Match info (number, arena, time)
- Right: Status badge (LIVE pulsing / SCHEDULED gray / ENDED muted)
- Hover: Slight scale + shadow increase
- Active/Selected: Primary color border

### Chat Area
- Height: 200px
- Messages: Stacked, newest at bottom
- Each message: Username (accent color) + message text
- Input: Fixed at bottom, rounded, dark input field

## 6. Technical Approach

### Stack
- Single HTML file with embedded CSS and JavaScript
- Vanilla JS (no framework needed for this scope)
- CSS Grid + Flexbox for layout
- CSS Custom Properties for theming
- LocalStorage for saving selected arena preference

### Data Structure
```javascript
// Arena
{ id: string, name: string, matches: Match[] }

// Match
{
  id: string,
  arena: string,
  matchNumber: number,
  status: 'live' | 'scheduled' | 'ended',
  meron: { name: string, odds: number },
  wala: { name: string, odds: number },
  bdd: number, // odds for tie
  startTime: Date
}

// ChatMessage
{ username: string, message: string, timestamp: Date }
```

### Simulated Data
- 5 arenas with 3-5 matches each
- Random odds between 0.80 - 1.20
- Fake chat messages rotating
- Simulated "LIVE" updates (random status changes)

### Performance Considerations
- CSS containment for list items
- Throttled scroll handlers
- Lazy load images (placeholder)
- Minimal DOM updates
