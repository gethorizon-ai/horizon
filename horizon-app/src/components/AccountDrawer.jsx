import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import KeyIcon from '@mui/icons-material/Key';
import { useLocation, useNavigate } from 'react-router-dom';
import { MenuItem } from '@mui/material';
import { useTheme } from '@emotion/react';

const drawerWidth = 240;

export default function AccountDrawer() {
  const theme = useTheme();
  console.log(theme.spacing);

  const navigate = useNavigate();
  const { pathname } = useLocation();

  const drawerItemsIconsHandlers = {
    'Getting started': {
      'icon': <KeyIcon />,
      'path': "/account/welcome"
    }
  };

  function goToPage(item) {
    return (() => { navigate(drawerItemsIconsHandlers[item]['path']) })
  };

  return (
    <Drawer
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
      variant="permanent"
      anchor="left"
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto', pt: 2 }}>
        <List>
          {Object.keys(drawerItemsIconsHandlers).map((item) => (
            <MenuItem key={item}
              onClick={goToPage(item)}
              selected={pathname === drawerItemsIconsHandlers[item]['path']}
              sx={{
                "&.Mui-selected": {
                  backgroundColor: theme.palette.secondary.light
                }
              }}
            >
              <ListItemText primary={item} sx={{ pl: 1 }} />
            </MenuItem>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}
