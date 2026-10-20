import { Composition, staticFile } from "remotion";
import { Reel, ReelProps } from "./Reel";

const FPS = 30;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Reel3IAs"
    component={Reel}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={FPS * 30}
    defaultProps={
      {
        starts: [0, 3.4, 7.2, 12, 16.8, 21.8, 25.6],
        ends: [3.2, 7, 11.8, 16.6, 21.6, 25.4, 29],
        total: 30,
        hasVoice: false,
      } satisfies ReelProps
    }
    calculateMetadata={async () => {
      const d = await (await fetch(staticFile("timing.json"))).json();
      const props: ReelProps = {
        starts: d.starts,
        ends: d.ends,
        total: d.total,
        hasVoice: Boolean(d.voice),
      };
      return { durationInFrames: Math.ceil(d.total * FPS), props };
    }}
  />
);
