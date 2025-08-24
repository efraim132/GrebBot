import {Box, Button, Heading} from "@primer/react";
import DiscordIcon from "./DiscordIcon.tsx";

interface Props {
    toggleBannerFunction: () => void;
}

function WarningBanner({toggleBannerFunction}: Props) {
  return (
      <Box
          sx={{
              border: '1px solid',
              borderColor: 'border.default',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              mb: 4,
              bg: 'canvas.default',
          }}
      >
          <Box sx={{mb: 2}}>
              <DiscordIcon size={"large"}/>
          </Box>
          <Heading as="h2" sx={{mb: 2}}>Welcome to GrebBot</Heading>
          <Box as="p" sx={{mb: 3, color: 'fg.muted'}}>
              Please Ensure that you know what you're doing, otherwise you may irreperably damage your Discord
              bot configuration
          </Box>
          <Box sx={{display: 'flex', justifyContent: 'center'}}>
              <Button onClick={toggleBannerFunction} variant="danger">Proceed</Button>
          </Box>
      </Box>
  );
}
export default WarningBanner;